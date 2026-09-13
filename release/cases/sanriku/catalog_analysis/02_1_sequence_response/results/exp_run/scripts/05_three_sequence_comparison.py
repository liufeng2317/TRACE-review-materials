from __future__ import annotations

import json
import shutil
import sys
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
STEP3_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison")

SUMMARY_CSV = STEP3_OUTPUT_DIR / "sequence_diagnostics_metrics.csv"
COMPARISON_CSV = STEP3_OUTPUT_DIR / "three_sequence_comparison.csv"
CONTROL_CSV = STEP3_OUTPUT_DIR / "control_summary.csv"
ROBUSTNESS_CSV = STEP3_OUTPUT_DIR / "robustness_summary.csv"
GRID_CSV = STEP3_OUTPUT_DIR / "parameter_grid_summary.csv"
STABILITY_CSV = STEP3_OUTPUT_DIR / "stability_flags.csv"
FEATURE_FLAGS_CSV = STEP3_OUTPUT_DIR / "stability_feature_flags.csv"
VERIFICATION_JSON = STEP3_OUTPUT_DIR / "robustness_verification.json"
ALT_STEP2_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics")
ALT_SUMMARY_CSV = ALT_STEP2_DIR / "sequence_diagnostics_metrics.csv"
ALT_COMPARISON_CSV = ALT_STEP2_DIR / "three_sequence_comparison.csv"
ALT_CONTROL_CSV = ALT_STEP2_DIR / "control_summary.csv"
ALT_ROBUSTNESS_CSV = ALT_STEP2_DIR / "robustness_summary.csv"
ALT_GRID_CSV = ALT_STEP2_DIR / "parameter_grid_summary.csv"
ALT_STABILITY_CSV = ALT_STEP2_DIR / "stability_flags.csv"
ALT_FEATURE_FLAGS_CSV = ALT_STEP2_DIR / "stability_feature_flags.csv"
FIGURE_DATA_DIR = STEP3_OUTPUT_DIR / "figure_data"

MASTER_SUMMARY_CSV = OUTPUT_DIR / "three_sequence_comparison_master.csv"
BASELINE_COMPARISON_CSV = OUTPUT_DIR / "three_sequence_comparison_baseline.csv"
ROBUSTNESS_OUT_CSV = OUTPUT_DIR / "robustness_across_definitions.csv"
SENSITIVITY_OUT_CSV = OUTPUT_DIR / "parameter_sensitivity_summary.csv"
STABILITY_OUT_CSV = OUTPUT_DIR / "feature_stability_summary.csv"
CONTROL_OUT_CSV = OUTPUT_DIR / "control_comparison_summary.csv"
GRID_OUT_CSV = OUTPUT_DIR / "parameter_grid_summary.csv"
SUMMARY_METRICS_CSV = OUTPUT_DIR / "sequence_metrics_summary.csv"
FIGURE_DATA_OUT_DIR = OUTPUT_DIR / "figure_data"
FIGURE_DIR = OUTPUT_DIR / "figures"

MAIN_FILE = BASE_DIR / "catalog/main_earthquake.csv"
CATALOG_FILE = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MECH_FILE = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_FILE = BASE_DIR / "stations/station.sta"

MAINSHOCKS = ["M1", "M2", "M3"]
BASELINE_RADIUS = 50.0
BASELINE_TIME = 90.0
BASELINE_DEPTH = "all"
FIGSIZE = (8.5, 5.5)
DPI = 300


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
    removed = 0
    for p in OUTPUT_DIR.glob("*"):
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        removed += 1
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DATA_OUT_DIR.mkdir(parents=True, exist_ok=True)
    log(f"[0] Cleaned {removed} stale artifacts in {OUTPUT_DIR}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return pd.read_csv(path)


def parse_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * r * np.arcsin(np.sqrt(a))


def load_mainshocks() -> pd.DataFrame:
    df = read_csv(MAIN_FILE)
    if "index" in df.columns:
        df = df.rename(columns={"index": "mainshock"})
    elif "mainshock" not in df.columns:
        df = df.iloc[:, :6]
        df.columns = ["mainshock", "datetime", "lat", "lon", "dep", "mag"]
    df["time"] = parse_time(df["datetime"])
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["dep"] = pd.to_numeric(df["dep"], errors="coerce")
    df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
    return df[["mainshock", "time", "lat", "lon", "dep", "mag"]].copy()


def load_catalog() -> pd.DataFrame:
    df = read_csv(CATALOG_FILE)
    df["time"] = parse_time(df["datetime"])
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df["dep"] = pd.to_numeric(df["dep"], errors="coerce")
    df["mag"] = pd.to_numeric(df["mag"], errors="coerce")
    df = df.sort_values("time").reset_index(drop=True)
    df["event_id"] = np.arange(len(df), dtype=int)
    return df


def load_mech() -> pd.DataFrame:
    df = read_csv(MECH_FILE)
    df["origin_time"] = parse_time(df["origin_time"])
    for c in ["lat_deg", "lon_deg", "depth_km", "mag_1", "mag_2", "n_hypo_stations", "focal_mech_score", "n_mech_stations"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def load_stations() -> pd.DataFrame:
    df = read_csv(STATION_FILE)
    for c in ["latitude", "longitude", "elevation_m"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "matched" in df.columns:
        df["matched"] = df["matched"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


def verify_fields(catalog: pd.DataFrame, main: pd.DataFrame, mech: pd.DataFrame, sta: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("catalog", catalog, ["time", "lat", "lon", "dep", "mag", "event_id"]),
        ("main_earthquake", main, ["mainshock", "time", "lat", "lon", "dep", "mag"]),
        ("mechanism", mech, ["origin_time", "lat_deg", "lon_deg", "depth_km"]),
        ("stations", sta, ["station_code", "latitude", "longitude", "matched"]),
    ]
    rows = []
    for name, df, req in checks:
        rows.append({"file": name, "n_rows": int(len(df)), "required_fields": json.dumps(req), "present_fields": json.dumps([c for c in req if c in df.columns]), "missing_fields": json.dumps([c for c in req if c not in df.columns])})
    return pd.DataFrame(rows)


def rematch_mainshocks(main: pd.DataFrame, catalog: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, m in main.iterrows():
        dt = abs((catalog["time"] - m["time"]).dt.total_seconds()) / 60.0
        dkm = haversine_km(m["lat"], m["lon"], catalog["lat"], catalog["lon"])
        dep = np.abs(catalog["dep"] - m["dep"])
        score = dt / 60.0 + dkm / 20.0 + dep / 30.0
        idx = score.nsmallest(5).index
        best = catalog.loc[idx[0]]
        rows.append({
            "mainshock": m["mainshock"],
            "ref_time": m["time"],
            "ref_lat": m["lat"],
            "ref_lon": m["lon"],
            "ref_dep": m["dep"],
            "ref_mag": m["mag"],
            "matched_event_id": int(best["event_id"]),
            "matched_time": best["time"],
            "matched_lat": float(best["lat"]),
            "matched_lon": float(best["lon"]),
            "matched_dep": float(best["dep"]),
            "matched_mag": float(best["mag"]),
            "time_shift_minutes": float((best["time"] - m["time"]).total_seconds() / 60.0),
            "horizontal_shift_km": float(haversine_km(m["lat"], m["lon"], best["lat"], best["lon"])),
            "depth_shift_km": float(best["dep"] - m["dep"]),
            "match_score": float(score.iloc[idx[0]]),
            "n_close_candidates": int((score < score.iloc[idx[0]] + 0.5).sum()),
            "close_candidates": json.dumps(idx.tolist()),
        })
    return pd.DataFrame(rows)


def baseline_slice(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.copy()
    s["mag_threshold"] = pd.to_numeric(s["mag_threshold"], errors="coerce")
    mask = (
        (s["radius_km"] == BASELINE_RADIUS)
        & (s["time_window_days"] == BASELINE_TIME)
        & (s["depth_strategy"] == BASELINE_DEPTH)
        & (s["mag_threshold"].isna())
    )
    out = s.loc[mask].copy()
    if out.empty:
        out = s.groupby("mainshock", as_index=False).first()
    return out


def load_inputs():
    summary_path = None
    for candidate in [SUMMARY_CSV, ALT_SUMMARY_CSV]:
        if candidate.exists():
            summary_path = candidate
            break
    if summary_path is None:
        raise FileNotFoundError(
            f"Missing Task 04 summary CSV; searched {SUMMARY_CSV} and {ALT_SUMMARY_CSV}"
        )

    comparison_path = COMPARISON_CSV if COMPARISON_CSV.exists() else ALT_COMPARISON_CSV
    control_path = CONTROL_CSV if CONTROL_CSV.exists() else ALT_CONTROL_CSV
    robustness_path = ROBUSTNESS_CSV if ROBUSTNESS_CSV.exists() else ALT_ROBUSTNESS_CSV
    grid_path = GRID_CSV if GRID_CSV.exists() else ALT_GRID_CSV
    stability_path = STABILITY_CSV if STABILITY_CSV.exists() else ALT_STABILITY_CSV
    feature_flags_path = FEATURE_FLAGS_CSV if FEATURE_FLAGS_CSV.exists() else ALT_FEATURE_FLAGS_CSV

    path_map = {
        "comparison": comparison_path,
        "control": control_path,
        "robustness": robustness_path,
        "grid": grid_path,
        "stability": stability_path,
        "feature_flags": feature_flags_path,
    }
    missing = [name for name, path in path_map.items() if path is None or not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required Task 04 outputs for: " + ", ".join(missing) +
            f"; searched {STEP3_OUTPUT_DIR} and {ALT_STEP2_DIR}"
        )

    summary = read_csv(summary_path)
    comparison = read_csv(comparison_path)
    control = read_csv(control_path)
    robustness = read_csv(robustness_path)
    grid = read_csv(grid_path)
    stability = read_csv(stability_path)
    feature_flags = read_csv(feature_flags_path)
    verification = json.loads(VERIFICATION_JSON.read_text()) if VERIFICATION_JSON.exists() else {}
    return summary, comparison, control, robustness, grid, stability, feature_flags, verification


def summary_metrics(summary: pd.DataFrame) -> pd.DataFrame:
    base = baseline_slice(summary)
    rows = []
    for mainshock, sdf in base.groupby("mainshock"):
        row = sdf.iloc[0]
        rows.append({
            "mainshock": mainshock,
            "n_total": int(row["n_total"]),
            "n_pre": int(row["n_pre"]),
            "n_post": int(row["n_post"]),
            "pre_rate": float(row["pre_rate"]),
            "post_rate": float(row["post_rate"]),
            "rate_ratio": float(row["rate_ratio"]),
            "moving_rate_max": float(row["moving_rate_max"]),
            "moving_rate_median": float(row["moving_rate_median"]),
            "burstiness_index": float(row["moving_rate_max"] / row["moving_rate_median"] if pd.notna(row["moving_rate_median"]) and row["moving_rate_median"] > 0 else np.nan),
            "post_omori_p": float(row["post_omori_p"]),
            "post_omori_r2": float(row["post_omori_r2"]),
            "radial_q50_km": float(row.get("radial_q50_km", np.nan)),
            "depth_q50_km": float(row.get("depth_q50_km", np.nan)),
            "mag_q50": float(row.get("mag_q50", np.nan)),
            "mecha_overlap_count": int(row.get("mecha_overlap_count", 0)) if pd.notna(row.get("mecha_overlap_count", 0)) else 0,
            "stations_within_100km": int(row.get("stations_within_100km", 0)) if pd.notna(row.get("stations_within_100km", 0)) else 0,
        })
    return pd.DataFrame(rows)


def compare_mainshocks(summary: pd.DataFrame) -> pd.DataFrame:
    base = baseline_slice(summary)
    rows = []
    for _, row in base.iterrows():
        rows.append({
            "mainshock": row["mainshock"],
            "background_level": float(row["n_pre"] / 90.0),
            "pre_activity": float(row["pre_rate"]),
            "post_activity": float(row["post_rate"]),
            "burstiness_index": float(row["moving_rate_max"] / row["moving_rate_median"] if pd.notna(row["moving_rate_median"]) and row["moving_rate_median"] > 0 else np.nan),
            "aftershock_decay_p": float(row["post_omori_p"]),
            "aftershock_decay_r2": float(row["post_omori_r2"]),
            "spatial_concentration_q50": float(row.get("radial_q50_km", np.nan)),
            "depth_structure_q50": float(row.get("depth_q50_km", np.nan)),
            "median_magnitude": float(row.get("mag_q50", np.nan)),
            "mechanism_overlap": int(row.get("mecha_overlap_count", 0)) if pd.notna(row.get("mecha_overlap_count", 0)) else 0,
        })
    out = pd.DataFrame(rows)
    order = {m: i for i, m in enumerate(MAINSHOCKS)}
    return out.sort_values("mainshock", key=lambda s: s.map(order)).reset_index(drop=True)


def robustness_summary(robustness: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mainshock, sdf in robustness.groupby("mainshock"):
        for metric in ["rate_ratio", "moving_rate_max", "post_omori_p", "radial_iqr_km", "depth_iqr_km"]:
            vals = pd.to_numeric(sdf[metric], errors="coerce").dropna()
            if vals.empty:
                continue
            rows.append({
                "mainshock": mainshock,
                "metric": metric,
                "median": float(vals.median()),
                "mean": float(vals.mean()),
                "iqr": float(vals.quantile(0.75) - vals.quantile(0.25)),
                "min": float(vals.min()),
                "max": float(vals.max()),
                "n": int(len(vals)),
                "robust_fraction": float((vals > 1.0).mean()) if metric == "rate_ratio" else float(vals.notna().mean()),
            })
    return pd.DataFrame(rows)


def control_summary(control: pd.DataFrame) -> pd.DataFrame:
    if control.empty:
        return control
    return control.copy()


def sensitivity_summary(grid: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mainshock, sdf in grid.groupby("mainshock"):
        for param in ["radius_km", "time_window_days", "depth_strategy", "mag_threshold"]:
            vals = sdf[param].dropna().unique()
            rr = pd.to_numeric(sdf["rate_ratio"], errors="coerce")
            rows.append({
                "mainshock": mainshock,
                "parameter": param,
                "n_levels": int(len(vals)),
                "rate_ratio_median": float(rr.median()),
                "rate_ratio_iqr": float(rr.quantile(0.75) - rr.quantile(0.25)),
                "post_omori_p_median": float(pd.to_numeric(sdf["post_omori_p"], errors="coerce").median()),
                "sparse_fraction": float(pd.to_numeric(sdf["n_total"], errors="coerce").lt(15).mean()),
            })
    return pd.DataFrame(rows)


def plot_event_centered_maps(catalog: pd.DataFrame, main: pd.DataFrame, match: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    last_scatter = None
    for ax, mname in zip(axes, MAINSHOCKS):
        mr = main[main["mainshock"] == mname].iloc[0]
        subset = catalog[(catalog["time"] >= mr["time"] - pd.Timedelta(days=90)) & (catalog["time"] <= mr["time"] + pd.Timedelta(days=90))]
        if subset.empty:
            ax.set_axis_off()
            continue
        x = subset["lon"]
        y = subset["lat"]
        c = subset["mag"]
        last_scatter = ax.scatter(x, y, c=c, s=np.clip((c.fillna(0) + 1.0) ** 2, 8, 60), cmap="viridis", alpha=0.75, edgecolors="none")
        ax.scatter([mr["lon"]], [mr["lat"]], marker="*", s=220, c="red", edgecolors="k", linewidths=0.6, zorder=5)
        ax.set_title(f"{mname} event-centered map")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(alpha=0.2)
    if last_scatter is not None:
        cbar = fig.colorbar(last_scatter, ax=axes.ravel().tolist(), shrink=0.92, pad=0.02)
        cbar.set_label("Magnitude")
    fig.savefig(FIGURE_DIR / "01_event_centered_maps.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_baseline_comparison(summary: pd.DataFrame) -> None:
    base = baseline_slice(summary)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    for ax, col, ylabel in zip(axes, ["n_pre", "n_post", "rate_ratio"], ["Pre-event count", "Post-event count", "Post/Pre rate ratio"]):
        ax.bar(base["mainshock"], base[col], color=["#4c78a8", "#f58518", "#54a24b"])
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel)
        ax.grid(axis="y", alpha=0.25)
    fig.savefig(FIGURE_DIR / "02_baseline_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_sensitivity_heatmaps(grid: pd.DataFrame) -> None:
    for metric, fname in [("rate_ratio", "03_rate_ratio_heatmap.png"), ("moving_rate_max", "04_rate_heatmap.png")]:
        fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)
        for ax, mname in zip(axes, MAINSHOCKS):
            sdf = grid[grid["mainshock"] == mname].copy()
            pivot = sdf.pivot_table(index="time_window_days", columns="radius_km", values=metric, aggfunc="mean")
            if pivot.empty:
                ax.set_axis_off()
                continue
            im = ax.imshow(pivot.values, aspect="auto", origin="lower", cmap="magma")
            ax.set_xticks(np.arange(len(pivot.columns)))
            ax.set_xticklabels([f"{v:.0f}" for v in pivot.columns], rotation=45)
            ax.set_yticks(np.arange(len(pivot.index)))
            ax.set_yticklabels([f"{v:.0f}" for v in pivot.index])
            ax.set_title(f"{mname}")
            ax.set_xlabel("Radius (km)")
            ax.set_ylabel("Time window (d)")
        cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.92)
        cbar.set_label(metric)
        fig.savefig(FIGURE_DIR / fname, dpi=DPI, bbox_inches="tight")
        plt.close(fig)


def plot_depth_stratified(summary: pd.DataFrame) -> None:
    base = baseline_slice(summary)
    fig, ax = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    for mname, color in zip(MAINSHOCKS, ["#4c78a8", "#f58518", "#54a24b"]):
        sdf = base[base["mainshock"] == mname].iloc[0]
        ax.scatter(sdf["depth_q50_km"], sdf["rate_ratio"], s=120, color=color, label=mname, edgecolors="k", linewidths=0.4)
    ax.axhline(1.0, color="0.3", ls="--", lw=1)
    ax.set_xlabel("Median sequence depth (km)")
    ax.set_ylabel("Post/Pre rate ratio")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.savefig(FIGURE_DIR / "05_depth_vs_rate_ratio.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_three_sequence_summary(comp: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.0), constrained_layout=True)
    axes = axes.ravel()
    panels = [("post_activity", "Post activity"), ("burstiness_index", "Burstiness"), ("aftershock_decay_p", "Omori p"), ("spatial_concentration_q50", "Median radial distance")]
    for ax, (col, title) in zip(axes, panels):
        ax.bar(comp["mainshock"], comp[col], color=["#4c78a8", "#f58518", "#54a24b"])
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.25)
    fig.savefig(FIGURE_DIR / "06_three_sequence_summary.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_control(control: pd.DataFrame) -> None:
    if control.empty:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.2), constrained_layout=True)
    ax.bar(control["mainshock"], control["relative_control_rate"], color="#9c755f")
    ax.axhline(1.0, color="0.3", ls="--", lw=1)
    ax.set_ylabel("Observed pre-rate / control background rate")
    ax.set_title("Control comparison")
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(FIGURE_DIR / "07_control_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_ranked_sensitivity(grid: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.4), constrained_layout=True)
    data = []
    labels = []
    for mname in MAINSHOCKS:
        sdf = grid[grid["mainshock"] == mname]
        data.append(pd.to_numeric(sdf["rate_ratio"], errors="coerce").dropna().values)
        labels.append(mname)
    ax.boxplot(data, labels=labels, showmeans=True)
    ax.axhline(1.0, color="0.3", ls="--", lw=1)
    ax.set_ylabel("Rate ratio across parameter grid")
    ax.set_title("Rate-ratio sensitivity")
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(FIGURE_DIR / "08_rate_ratio_sensitivity.png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def save_outputs(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def main() -> None:
    clean_output_dir()
    log("[1] Loading source tables")
    catalog = load_catalog()
    main = load_mainshocks()
    mech = load_mech()
    sta = load_stations()
    ver = verify_fields(catalog, main, mech, sta)
    ver.to_csv(OUTPUT_DIR / "field_verification.csv", index=False)

    log("[2] Rematching mainshocks to relocated catalog")
    matched = rematch_mainshocks(main, catalog)
    matched.to_csv(OUTPUT_DIR / "mainshock_rematch.csv", index=False)

    log("[3] Loading Task 04 outputs")
    summary, comparison, control, robustness, grid, stability, feature_flags, verification = load_inputs()
    required_summary_cols = ["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "n_total", "n_pre", "n_post", "pre_rate", "post_rate", "rate_ratio", "moving_rate_max", "moving_rate_median", "post_omori_p", "post_omori_r2"]
    missing_summary = [c for c in required_summary_cols if c not in summary.columns]
    if missing_summary:
        raise RuntimeError(f"sequence diagnostics summary missing required columns: {missing_summary}")
    for df_name, df in [("comparison", comparison), ("control", control), ("robustness", robustness), ("grid", grid), ("stability", stability), ("feature_flags", feature_flags)]:
        if df.empty:
            raise RuntimeError(f"{df_name} input from Task 04 is empty; rerun prior task before Task 05")
    summary["mag_threshold"] = pd.to_numeric(summary["mag_threshold"], errors="coerce")
    summary_metrics_df = summary_metrics(summary)
    comparison_df = compare_mainshocks(summary)
    robustness_df = robustness.copy()
    sensitivity_df = sensitivity_summary(grid)
    stability_df = stability.copy()
    control_df = control.copy()

    log("[4] Writing derived comparison tables")
    save_outputs(summary_metrics_df, SUMMARY_METRICS_CSV)
    save_outputs(comparison_df, BASELINE_COMPARISON_CSV)
    save_outputs(robustness_df, ROBUSTNESS_OUT_CSV)
    save_outputs(sensitivity_df, SENSITIVITY_OUT_CSV)
    save_outputs(stability_df, STABILITY_OUT_CSV)
    save_outputs(control_df, CONTROL_OUT_CSV)
    save_outputs(grid, GRID_OUT_CSV)
    save_outputs(pd.concat([summary_metrics_df.assign(table="summary_metrics"), comparison_df.assign(table="comparison")], ignore_index=True, sort=False), MASTER_SUMMARY_CSV)

    log("[5] Saving figure-data tables")
    FIGURE_DATA_OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(FIGURE_DATA_OUT_DIR / "sequence_diagnostics_metrics.csv", index=False)
    comparison.to_csv(FIGURE_DATA_OUT_DIR / "three_sequence_comparison.csv", index=False)
    control.to_csv(FIGURE_DATA_OUT_DIR / "control_summary.csv", index=False)
    robustness.to_csv(FIGURE_DATA_OUT_DIR / "robustness_summary.csv", index=False)
    grid.to_csv(FIGURE_DATA_OUT_DIR / "parameter_grid_summary.csv", index=False)
    stability.to_csv(FIGURE_DATA_OUT_DIR / "stability_flags.csv", index=False)
    feature_flags.to_csv(FIGURE_DATA_OUT_DIR / "stability_feature_flags.csv", index=False)

    log("[6] Generating diagnostic figures")
    plot_event_centered_maps(catalog, main, matched)
    plot_baseline_comparison(summary)
    plot_sensitivity_heatmaps(grid)
    plot_depth_stratified(summary)
    plot_three_sequence_summary(comparison_df)
    plot_control(control_df)
    plot_ranked_sensitivity(grid)

    summary_out = {
        "source_verification": ver.to_dict(orient="records"),
        "rematch": matched.to_dict(orient="records"),
        "n_catalog": int(len(catalog)),
        "n_mechanism": int(len(mech)),
        "n_stations": int(len(sta)),
        "baseline_definition": {
            "radius_km": BASELINE_RADIUS,
            "time_window_days": BASELINE_TIME,
            "depth_strategy": BASELINE_DEPTH,
            "mag_threshold": None,
        },
        "mainshock_summary": comparison_df.to_dict(orient="records"),
    }
    (OUTPUT_DIR / "three_sequence_comparison_verification.json").write_text(json.dumps(summary_out, indent=2, default=to_jsonable), encoding="utf-8")

    log("[7] Figure outputs:")
    for p in sorted(FIGURE_DIR.glob("*.png")):
        log(f"    {p.name}")
    log("[8] Three-sequence comparison completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
