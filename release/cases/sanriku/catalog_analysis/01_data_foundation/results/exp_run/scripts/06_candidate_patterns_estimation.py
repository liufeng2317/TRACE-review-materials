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
from scipy.stats import spearmanr


DATA_DIR = Path(
    "<CASE_ROOT>/data"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/06_candidate_patterns_estimation"
)
STAGE1_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning"
)
MATCH_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching"
)
BACKGROUND_DIR = Path(
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
BACKGROUND_SUMMARY = BACKGROUND_DIR / "regional_summary_metrics.csv"
BACKGROUND_DEPTH_SEG = BACKGROUND_DIR / "regional_depth_segmentation.csv"
CONTEXT_SUMMARY = CONTEXT_DIR / "mainshock_context_summary.csv"
THRESHOLD_NOTES = CONTEXT_DIR / "sequence_threshold_notes.csv"

EARTH_RADIUS_KM = 6371.0088
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


def normalize_time(df: pd.DataFrame, col: str = "origin_time") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce", utc=True)
    return out


def coerce_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def load_tables() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cat = pd.read_csv(CLEAN_CATALOG, parse_dates=["origin_time"])
    main = pd.read_csv(CLEAN_MAIN, parse_dates=["origin_time"])
    mech = pd.read_csv(CLEAN_MECH, parse_dates=["origin_time"])
    sta = pd.read_csv(CLEAN_STATIONS)
    match = pd.read_csv(MATCH_TABLE, parse_dates=["origin_time", "matched_time"])
    bg = pd.read_csv(BACKGROUND_SUMMARY) if BACKGROUND_SUMMARY.exists() else pd.DataFrame()
    ctx = pd.read_csv(CONTEXT_SUMMARY) if CONTEXT_SUMMARY.exists() else pd.DataFrame()
    return cat, main, mech, sta, match, bg, ctx


def load_depth_segments() -> pd.DataFrame:
    if BACKGROUND_DEPTH_SEG.exists():
        return pd.read_csv(BACKGROUND_DEPTH_SEG)
    return pd.DataFrame(columns=["depth_min_km", "depth_max_km", "count"])


def summarize_catalog_patterns(cat: pd.DataFrame, bg: pd.DataFrame, ctx: pd.DataFrame, sta: pd.DataFrame, mech: pd.DataFrame, match: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cat = cat.copy()
    cat["origin_time"] = pd.to_datetime(cat["origin_time"], errors="coerce", utc=True)
    cat = cat.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"])
    cat["origin_time_naive"] = cat["origin_time"].dt.tz_convert(None)
    cat = cat.sort_values("origin_time_naive").reset_index(drop=True)

    duration_days = max((cat["origin_time_naive"].max() - cat["origin_time_naive"].min()).total_seconds() / 86400.0, 1.0)
    event_rate_per_day = len(cat) / duration_days
    if event_rate_per_day > 100:
        window_days = 30
    elif event_rate_per_day > 20:
        window_days = 90
    else:
        window_days = 180

    time_rate = cat.set_index("origin_time_naive").resample(f"{window_days}D").size().reset_index(name="event_count")
    time_rate["events_per_day"] = time_rate["event_count"] / window_days
    time_rate["rolling_mean_3"] = time_rate["event_count"].rolling(3, center=True, min_periods=1).mean()

    cat["year"] = cat["origin_time_naive"].dt.year
    cat["month"] = cat["origin_time_naive"].dt.to_period("M").astype(str)
    cat["day"] = cat["origin_time_naive"].dt.date

    lat_q = cat["latitude"].quantile([0.25, 0.5, 0.75]).to_dict()
    lon_q = cat["longitude"].quantile([0.25, 0.5, 0.75]).to_dict()
    depth_q = cat["depth_km"].quantile([0.25, 0.5, 0.75]).to_dict()
    mag_q = cat["magnitude"].quantile([0.25, 0.5, 0.75]).to_dict()

    spatial_clusters = []
    for label, lat_range, lon_range in [
        ("NW", (cat["latitude"].min(), lat_q[0.25]), (cat["longitude"].min(), lon_q[0.25])),
        ("Central", (lat_q[0.25], lat_q[0.75]), (lon_q[0.25], lon_q[0.75])),
        ("SE", (lat_q[0.75], cat["latitude"].max()), (lon_q[0.75], cat["longitude"].max())),
    ]:
        mask = cat["latitude"].between(*lat_range) & cat["longitude"].between(*lon_range)
        spatial_clusters.append({
            "region": label,
            "count": int(mask.sum()),
            "fraction": float(mask.mean()),
            "median_depth_km": float(cat.loc[mask, "depth_km"].median()) if mask.any() else np.nan,
            "median_magnitude": float(cat.loc[mask, "magnitude"].median()) if mask.any() else np.nan,
        })

    depth_segments = load_depth_segments()
    if len(depth_segments) == 0:
        depth_bins = np.unique(np.quantile(cat["depth_km"], [0, 0.25, 0.5, 0.75, 1.0]))
        depth_segments = pd.DataFrame({"depth_min_km": depth_bins[:-1], "depth_max_km": depth_bins[1:]})
    depth_summary = []
    for _, seg in depth_segments.iterrows():
        mask = cat["depth_km"].between(seg["depth_min_km"], seg["depth_max_km"], inclusive="both")
        depth_summary.append({
            "depth_min_km": float(seg["depth_min_km"]),
            "depth_max_km": float(seg["depth_max_km"]),
            "count": int(mask.sum()),
            "fraction": float(mask.mean()),
            "median_magnitude": float(cat.loc[mask, "magnitude"].median()) if mask.any() else np.nan,
        })
    depth_summary = pd.DataFrame(depth_summary)

    magnitude_bins = np.arange(np.floor(cat["magnitude"].min() * 10) / 10.0, np.ceil(cat["magnitude"].max() * 10) / 10.0 + 0.1, 0.1)
    mag_hist, mag_edges = np.histogram(cat["magnitude"].values, bins=magnitude_bins)
    mag_centers = mag_edges[:-1] + 0.05

    depth_mag_corr = spearmanr(cat["depth_km"], cat["magnitude"], nan_policy="omit")
    lat_mag_corr = spearmanr(cat["latitude"], cat["magnitude"], nan_policy="omit")
    lon_mag_corr = spearmanr(cat["longitude"], cat["magnitude"], nan_policy="omit")

    nearby_station = []
    if len(sta):
        sample = cat.sample(n=min(2000, len(cat)), random_state=5)
        for _, ev in sample.iterrows():
            d = haversine_km(sta["longitude"].values, sta["latitude"].values, ev["longitude"], ev["latitude"])
            nearby_station.append(np.min(d))
    nearby_station = np.asarray(nearby_station) if len(nearby_station) else np.asarray([])

    mech_geom_cols = [c for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"] if c in mech.columns]
    mech_core_cols = [c for c in ["strike_plane1", "dip_plane1", "rake_plane1"] if c in mech.columns]
    mech_geom = mech[mech_geom_cols].notna().any(axis=1) if mech_geom_cols else pd.Series(False, index=mech.index)
    mech_core = mech[mech_core_cols].notna().all(axis=1) if len(mech_core_cols) == 3 else pd.Series(False, index=mech.index)
    mech_summary = pd.DataFrame([
        {"metric": "mechanism_records", "value": len(mech)},
        {"metric": "mechanism_geometry_available", "value": int(mech_geom.sum())},
        {"metric": "mechanism_core_available", "value": int(mech_core.sum())},
        {"metric": "mechanism_geometry_fraction", "value": float(mech_geom.mean()) if len(mech) else np.nan},
        {"metric": "mechanism_core_fraction", "value": float(mech_core.mean()) if len(mech) else np.nan},
        {"metric": "station_count", "value": len(sta)},
        {"metric": "median_nearest_station_km", "value": float(np.median(nearby_station)) if len(nearby_station) else np.nan},
        {"metric": "p90_nearest_station_km", "value": float(np.quantile(nearby_station, 0.9)) if len(nearby_station) else np.nan},
        {"metric": "depth_magnitude_spearman_rho", "value": float(depth_mag_corr.correlation) if np.isfinite(depth_mag_corr.correlation) else np.nan},
        {"metric": "depth_magnitude_spearman_p", "value": float(depth_mag_corr.pvalue) if np.isfinite(depth_mag_corr.pvalue) else np.nan},
        {"metric": "latitude_magnitude_spearman_rho", "value": float(lat_mag_corr.correlation) if np.isfinite(lat_mag_corr.correlation) else np.nan},
        {"metric": "longitude_magnitude_spearman_rho", "value": float(lon_mag_corr.correlation) if np.isfinite(lon_mag_corr.correlation) else np.nan},
    ])

    dominant_depth_segments = depth_summary.sort_values("count", ascending=False).head(2).copy()
    if len(dominant_depth_segments) == 0 and len(depth_summary):
        dominant_depth_segments = depth_summary.head(1).copy()
    dominant_regions = pd.DataFrame(spatial_clusters).sort_values("count", ascending=False).head(3).copy()
    if len(dominant_regions) == 0:
        dominant_regions = pd.DataFrame([{"region": "n/a", "count": 0, "fraction": 0.0}])

    burst_threshold = time_rate["event_count"].median() + 1.5 * time_rate["event_count"].std(ddof=1)
    burst_periods = time_rate.loc[time_rate["event_count"] >= burst_threshold, ["origin_time_naive", "event_count"]].copy() if len(time_rate) else pd.DataFrame(columns=["origin_time_naive", "event_count"])
    quiet_threshold = time_rate["event_count"].median() - 1.0 * time_rate["event_count"].std(ddof=1)
    quiet_periods = time_rate.loc[time_rate["event_count"] <= quiet_threshold, ["origin_time_naive", "event_count"]].copy() if len(time_rate) else pd.DataFrame(columns=["origin_time_naive", "event_count"])

    candidate_rows = []
    candidate_rows.append({
        "pattern_id": "P01",
        "pattern_type": "spatial_cluster",
        "scope": "catalog",
        "evidence": f"Top spatial density zones concentrate {dominant_regions.iloc[0]['fraction']:.1%} of events in region {dominant_regions.iloc[0]['region']}",
        "priority_score": float(dominant_regions.iloc[0]["count"] / len(cat)),
        "followup_suggestion": "Test cluster-specific catalogs and use spatial masks or local search radii for sequence analysis.",
    })
    candidate_rows.append({
        "pattern_id": "P02",
        "pattern_type": "temporal_burst_or_quiet_period",
        "scope": "catalog",
        "evidence": f"Using {window_days}-day bins, {len(burst_periods)} burst windows and {len(quiet_periods)} quiet windows exceed median-based thresholds.",
        "priority_score": float(min(1.0, (len(burst_periods) + len(quiet_periods)) / max(len(time_rate), 1))),
        "followup_suggestion": "Run change-point or moving-window rate tests around burst and quiet intervals.",
    })
    if len(dominant_depth_segments) >= 2:
        depth_evidence = f"Two deepest populated depth bins contain {dominant_depth_segments.iloc[0]['fraction']:.1%} and {dominant_depth_segments.iloc[1]['fraction']:.1%} of events."
    else:
        depth_evidence = f"Single populated depth bin contains {dominant_depth_segments.iloc[0]['fraction']:.1%} of events."
    candidate_rows.append({
        "pattern_id": "P03",
        "pattern_type": "depth_segmentation",
        "scope": "catalog",
        "evidence": depth_evidence,
        "priority_score": float(dominant_depth_segments["count"].sum() / len(cat)),
        "followup_suggestion": "Split later analyses by empirical depth bins; test shallow vs intermediate-depth behavior separately.",
    })
    candidate_rows.append({
        "pattern_id": "P04",
        "pattern_type": "magnitude_depth_space_relationship",
        "scope": "catalog",
        "evidence": f"Spearman rho(depth, magnitude)={depth_mag_corr.correlation:.2f}; rho(lat, magnitude)={lat_mag_corr.correlation:.2f}; rho(lon, magnitude)={lon_mag_corr.correlation:.2f}.",
        "priority_score": float(abs(depth_mag_corr.correlation) if np.isfinite(depth_mag_corr.correlation) else 0.0),
        "followup_suggestion": "Test magnitude conditioning by depth and position before applying a single catalog-wide threshold.",
    })
    if len(nearby_station):
        median_station = float(np.median(nearby_station))
        p90_station = float(np.quantile(nearby_station, 0.9))
    else:
        median_station = np.nan
        p90_station = np.nan
    candidate_rows.append({
        "pattern_id": "P05",
        "pattern_type": "station_coverage_effect",
        "scope": "catalog",
        "evidence": f"Median nearest-station distance is {median_station:.1f} km with p90 {p90_station:.1f} km." if np.isfinite(median_station) and np.isfinite(p90_station) else "No station-distance sample available.",
        "priority_score": float(np.clip((p90_station if np.isfinite(p90_station) else 0.0) / 100.0, 0, 1)),
        "followup_suggestion": "Apply station-coverage masks or uncertainty inflation where nearest-station distances are large.",
    })
    geom_frac = float(mech_summary.loc[mech_summary.metric == "mechanism_geometry_fraction", "value"].iloc[0]) if (len(mech_summary) and (mech_summary.metric == "mechanism_geometry_fraction").any()) else np.nan
    core_frac = float(mech_summary.loc[mech_summary.metric == "mechanism_core_fraction", "value"].iloc[0]) if (len(mech_summary) and (mech_summary.metric == "mechanism_core_fraction").any()) else np.nan
    candidate_rows.append({
        "pattern_id": "P06",
        "pattern_type": "focal_mechanism_data_gap",
        "scope": "catalog",
        "evidence": f"Mechanism geometry available for {geom_frac:.1%} of mechanism records; core mechanisms for {core_frac:.1%}." if np.isfinite(geom_frac) and np.isfinite(core_frac) else "Mechanism availability metrics unavailable.",
        "priority_score": float(1.0 - geom_frac) if np.isfinite(geom_frac) else 0.0,
        "followup_suggestion": "Treat mechanism analysis as sparse; separate availability from geometry-property interpretation.",
    })

    if len(ctx):
        ctx = ctx.copy()
        required_ctx_cols = ["density_ratio_to_regional_median", "station_count_local", "mechanism_local_records", "local_event_count", "depth_domain_flag", "sequence_threshold_note"]
        for col in required_ctx_cols:
            if col not in ctx.columns:
                ctx[col] = np.nan if col != "sequence_threshold_note" else ""
        ctx["density_vs_regional"] = pd.to_numeric(ctx.get("density_ratio_to_regional_median"), errors="coerce")
        ctx["station_count_local"] = pd.to_numeric(ctx.get("station_count_local"), errors="coerce")
        ctx["mechanism_local_records"] = pd.to_numeric(ctx.get("mechanism_local_records"), errors="coerce")
        ctx["local_event_count"] = pd.to_numeric(ctx.get("local_event_count"), errors="coerce")
        for _, row in ctx.iterrows():
            rid = str(row.get("reference_id", ""))
            candidate_rows.append({
                "pattern_id": f"MS_{rid}",
                "pattern_type": "mainshock_local_context",
                "scope": rid,
                "evidence": f"Local density ratio={row.get('density_ratio_to_regional_median', np.nan):.2f}, stations={int(row.get('station_count_local', 0))}, mechanism records={int(row.get('mechanism_local_records', 0))}, depth flag={row.get('depth_domain_flag', '')}.",
                "priority_score": float(np.clip(abs(float(row.get('density_ratio_to_regional_median', 1.0)) - 1.0), 0, 3) / 3.0),
                "followup_suggestion": str(row.get("sequence_threshold_note", "")),
            })

    patterns = pd.DataFrame(candidate_rows)
    patterns["priority_rank"] = patterns["priority_score"].rank(method="dense", ascending=False).astype(int)
    patterns = patterns.sort_values(["priority_rank", "pattern_id"]).reset_index(drop=True)

    followup = pd.DataFrame([
        {
            "analysis_axis": "space",
            "suggested_threshold_or_mask": "Use spatial clusters and mainshock-centered windows; test compact radii for dense regions.",
            "why": "The catalog shows nonuniform spatial density and mainshock-specific local context differences.",
        },
        {
            "analysis_axis": "time",
            "suggested_threshold_or_mask": f"Use {window_days}-day windows for rate diagnostics; flag burst/quiet intervals.",
            "why": "Event rate changes are better resolved with adaptive bin widths tied to catalog density.",
        },
        {
            "analysis_axis": "depth",
            "suggested_threshold_or_mask": "Split analyses by empirical depth bins and mainshock depth domains.",
            "why": "Depth segmentation is visible in the background catalog and in mainshock contexts.",
        },
        {
            "analysis_axis": "magnitude",
            "suggested_threshold_or_mask": "Use Mc-informed thresholds for background screening; test event-specific magnitude cuts around mainshocks.",
            "why": "Preliminary completeness and b-value diagnostics imply a data-driven magnitude cutoff is preferable.",
        },
        {
            "analysis_axis": "coverage",
            "suggested_threshold_or_mask": "Downweight or mask areas with sparse station or focal-mechanism coverage.",
            "why": "Sampling biases can affect detectability, magnitude estimates, and mechanism availability.",
        },
    ])

    return patterns, followup


def plot_patterns(patterns: pd.DataFrame, outpath: Path) -> None:
    top = patterns.head(12).copy()
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    colors = ["#4daf4a" if "mainshock" not in t else "#e41a1c" for t in top["pattern_type"]]
    ax.barh(top["pattern_id"], top["priority_score"], color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Priority score")
    ax.set_ylabel("Candidate pattern")
    ax.set_title("Ranked candidate patterns for follow-up analysis")
    ax.grid(True, axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_context_overview(ctx: pd.DataFrame, outpath: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.4, 7.2))
    axs = axes.ravel()
    x = np.arange(len(ctx))
    axs[0].bar(x, ctx["local_event_count"], color="#4daf4a")
    axs[0].set_xticks(x)
    axs[0].set_xticklabels(ctx["reference_id"], rotation=0)
    axs[0].set_ylabel("Local event count")
    axs[0].set_title("Mainshock local density")
    axs[1].bar(x, ctx["station_count_local"], color="#377eb8")
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(ctx["reference_id"], rotation=0)
    axs[1].set_ylabel("Nearby stations")
    axs[1].set_title("Mainshock station coverage")
    axs[2].bar(x, ctx["mechanism_local_records"], color="#ff7f0e")
    axs[2].set_xticks(x)
    axs[2].set_xticklabels(ctx["reference_id"], rotation=0)
    axs[2].set_ylabel("Nearby mechanism records")
    axs[2].set_title("Mechanism availability")
    axs[3].bar(x, ctx["density_ratio_to_regional_median"], color="#984ea3")
    axs[3].axhline(1.0, color="k", lw=0.8, ls="--")
    axs[3].set_xticks(x)
    axs[3].set_xticklabels(ctx["reference_id"], rotation=0)
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

        cat, main, mech, sta, match, bg, ctx = load_tables()
        cat = coerce_numeric(normalize_time(cat), ["latitude", "longitude", "depth_km", "magnitude"])
        main = coerce_numeric(normalize_time(main), ["latitude", "longitude", "depth_km", "magnitude"])
        mech = coerce_numeric(normalize_time(mech), ["latitude", "longitude", "depth_km", "mag_1", "mag_2", "strike_plane1", "dip_plane1", "rake_plane1", "P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip"])
        sta = coerce_numeric(sta, ["latitude", "longitude", "elevation_m"])
        match = coerce_numeric(normalize_time(match), ["latitude", "longitude", "depth_km", "magnitude", "time_diff_sec", "distance_km", "depth_diff_km", "mag_diff", "candidate_count", "search_window_hours"])
        ctx = coerce_numeric(ctx, ["local_event_count", "station_count_local", "mechanism_local_records", "density_ratio_to_regional_median", "local_depth_median_km", "local_depth_iqr_km"]) if len(ctx) else ctx

        cat = cat.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
        main = main.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
        mech = mech.copy()
        sta = sta.dropna(subset=["latitude", "longitude"]).copy()
        match = match.copy()
        ctx = ctx.copy()

        patterns, followup = summarize_catalog_patterns(cat, bg, ctx, sta, mech, match)
        if len(patterns) == 0:
            raise ValueError("No candidate patterns were produced")
        if len(patterns) == 0:
            raise ValueError("No candidate patterns were produced")

        patterns.to_csv(OUTPUT_DIR / "candidate_patterns_ranked.csv", index=False)
        followup.to_csv(OUTPUT_DIR / "followup_analysis_suggestions.csv", index=False)
        bg.to_csv(OUTPUT_DIR / "background_summary_snapshot.csv", index=False)
        ctx.to_csv(OUTPUT_DIR / "mainshock_context_snapshot.csv", index=False)

        # Machine-readable synthesis table.
        synthesis = pd.DataFrame([
            {"item": "catalog_events", "value": len(cat)},
            {"item": "mainshock_events", "value": len(main)},
            {"item": "station_count", "value": len(sta)},
            {"item": "mechanism_records", "value": len(mech)},
            {"item": "major_matches", "value": len(match)},
            {"item": "pattern_count", "value": len(patterns)},
            {"item": "followup_axis_count", "value": len(followup)},
            {"item": "top_pattern_id", "value": patterns.iloc[0]["pattern_id"] if len(patterns) else ""},
            {"item": "top_pattern_type", "value": patterns.iloc[0]["pattern_type"] if len(patterns) else ""},
            {"item": "top_followup_axis", "value": followup.iloc[0]["analysis_axis"] if len(followup) else ""},
        ])
        synthesis.to_csv(OUTPUT_DIR / "candidate_patterns_summary.csv", index=False)

        plot_patterns(patterns, OUTPUT_DIR / "figure_candidate_patterns_ranked.png")
        plot_context_overview(ctx, OUTPUT_DIR / "figure_mainshock_context_overview.png")

        print("[06_candidate_patterns_estimation] Completed successfully.", flush=True)
        print(f"[06_candidate_patterns_estimation] Output directory: {OUTPUT_DIR}", flush=True)
        print(f"[06_candidate_patterns_estimation] Ranked patterns: {len(patterns)}", flush=True)
        print(f"[06_candidate_patterns_estimation] Mainshock context rows: {len(ctx)}", flush=True)
        print(f"[06_candidate_patterns_estimation] Top pattern: {patterns.iloc[0]['pattern_id'] if len(patterns) else 'n/a'}", flush=True)

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
