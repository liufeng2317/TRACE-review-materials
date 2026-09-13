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
import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
STEP2_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction")
STEP3_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics")
STEP4_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison")

CATALOG_PATH = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MAIN_PATH = BASE_DIR / "catalog/main_earthquake.csv"
MATCH_PATH = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/matched_mainshocks.csv")
SEQ_PATH = STEP2_OUTPUT_DIR / "event_centered_sequence_table.csv"
SUMMARY_PATH = STEP3_OUTPUT_DIR / "sequence_diagnostics_metrics.csv"
WINDOW_PATH = STEP3_OUTPUT_DIR / "time_binned_rates.csv"
RADIAL_PATH = STEP3_OUTPUT_DIR / "radial_distance_summary.csv"
DEPTH_PATH = STEP3_OUTPUT_DIR / "depth_distribution_summary.csv"
MAG_PATH = STEP3_OUTPUT_DIR / "magnitude_distribution_summary.csv"
MECHA_PATH = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_PATH = BASE_DIR / "stations/station.sta"
ROBUSTNESS_PATH = STEP4_OUTPUT_DIR / "robustness_summary.csv"

RANDOM_SEED = 202405
CONTROL_SHIFT_DAYS = 120.0
CONTROL_WINDOW_DAYS = 90.0
CONTROL_RADIUS_KM = 50.0
CONTROL_MAG_THRESHOLDS = [None, 1.2, 1.5, 2.0]
CONTROL_TIME_WINDOWS = [7.0, 30.0, 60.0, 90.0]
N_RANDOM_CONTROLS = 50
MIN_RATE_FOR_RATIO = 1e-12


def log(msg: str) -> None:
    print(msg, flush=True)


def clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    for pattern in ["*.csv", "*.json", "*.png", "*.txt"]:
        for p in OUTPUT_DIR.glob(pattern):
            if p.is_file() or p.is_symlink():
                p.unlink()
                removed += 1
            elif p.is_dir():
                shutil.rmtree(p)
                removed += 1
    for sub in ["figure_data", "figures"]:
        d = OUTPUT_DIR / sub
        if d.exists():
            shutil.rmtree(d)
            removed += 1
    (OUTPUT_DIR / "figure_data").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    log(f"[0] Cleaned {removed} stale artifacts in {OUTPUT_DIR}")


def parse_time(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", utc=True)


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * 6371.0 * np.arcsin(np.sqrt(a))


def load_inputs():
    cat = pd.read_csv(CATALOG_PATH)
    main = pd.read_csv(MAIN_PATH)
    match = pd.read_csv(MATCH_PATH)
    seq = pd.read_csv(SEQ_PATH)
    summary = pd.read_csv(SUMMARY_PATH)
    window = pd.read_csv(WINDOW_PATH)
    radial = pd.read_csv(RADIAL_PATH)
    depth = pd.read_csv(DEPTH_PATH)
    mag = pd.read_csv(MAG_PATH)
    mecha = pd.read_csv(MECHA_PATH)
    station = pd.read_csv(STATION_PATH, sep=None, engine="python")
    robustness = pd.read_csv(ROBUSTNESS_PATH) if ROBUSTNESS_PATH.exists() else pd.DataFrame()

    cat["datetime"] = parse_time(cat["datetime"])
    main["datetime"] = parse_time(main["datetime"])
    match["matched_datetime"] = parse_time(match["matched_datetime"])
    for df in [seq, window]:
        if "datetime" in df.columns:
            df["datetime"] = parse_time(df["datetime"])
    mecha["origin_time"] = parse_time(mecha["origin_time"])
    return cat, main, match, seq, summary, window, radial, depth, mag, mecha, station, robustness


def depth_mask(df: pd.DataFrame, mainshock_row: pd.Series, strategy: str) -> pd.Series:
    if strategy == "all":
        return pd.Series(True, index=df.index)
    if strategy == "mainshock_window":
        center = float(mainshock_row["matched_dep"])
        width = max(20.0, 0.75 * max(center, 1.0))
        return (df["dep"] >= center - width) & (df["dep"] <= center + width)
    if strategy == "stratified":
        center = float(mainshock_row["matched_dep"])
        if center < 25:
            lo, hi = 0.0, 25.0
        elif center < 45:
            lo, hi = 25.0, 45.0
        else:
            lo, hi = 45.0, 80.0
        return (df["dep"] >= lo) & (df["dep"] < hi)
    raise ValueError(strategy)


def add_seq_coords(df: pd.DataFrame, mainshock_row: pd.Series) -> pd.DataFrame:
    out = df.copy()
    out["time_rel_days"] = (out["datetime"] - mainshock_row["matched_datetime"]).dt.total_seconds() / 86400.0
    out["radial_distance_km"] = haversine_km(mainshock_row["matched_lat"], mainshock_row["matched_lon"], out["lat"].to_numpy(), out["lon"].to_numpy())
    out["depth_rel_km"] = out["dep"] - float(mainshock_row["matched_dep"])
    out["pre_post"] = np.where(out["time_rel_days"] < 0, "pre", np.where(out["time_rel_days"] > 0, "post", "mainshock"))
    return out


def pick_baseline(summary: pd.DataFrame, mainshock: str) -> pd.Series:
    sub = summary[(summary["mainshock"] == mainshock) & (summary["radius_km"] == CONTROL_RADIUS_KM) & (summary["time_window_days"] == CONTROL_WINDOW_DAYS)]
    sub = sub[sub["depth_strategy"].eq("all")]
    if "mag_threshold" in sub.columns:
        sub = sub[sub["mag_threshold"].isna() | (sub["mag_threshold"] == 1.2)]
    if sub.empty:
        sub = summary[summary["mainshock"] == mainshock]
    if sub.empty:
        raise RuntimeError(f"No baseline summary row for {mainshock}")
    sub = sub.sort_values(["mag_threshold", "n_total"], ascending=[True, False])
    return sub.iloc[0]


def make_control_window_times(main_dt: pd.Timestamp, cat_min: pd.Timestamp, cat_max: pd.Timestamp, rng: np.random.Generator) -> List[pd.Timestamp]:
    times = []
    safe_start = cat_min + pd.Timedelta(days=CONTROL_WINDOW_DAYS + 5)
    safe_end = cat_max - pd.Timedelta(days=CONTROL_WINDOW_DAYS + 5)
    left = main_dt - pd.Timedelta(days=CONTROL_SHIFT_DAYS)
    right = main_dt + pd.Timedelta(days=CONTROL_SHIFT_DAYS)
    candidates = [left, right]
    for cand in candidates:
        if safe_start <= cand <= safe_end:
            times.append(cand)
    if len(times) < 2:
        span_days = (safe_end - safe_start).total_seconds() / 86400.0
        if span_days > 1:
            for _ in range(2 - len(times)):
                frac = rng.uniform(0.15, 0.85)
                times.append(safe_start + pd.Timedelta(days=span_days * frac))
    return times[:2]


def compute_rate(seq: pd.DataFrame, tdays: float, radius_km: float, mag_thr: Optional[float], mainshock_row: pd.Series) -> Dict[str, float]:
    subset = add_seq_coords(seq, mainshock_row)
    subset = subset[(subset["radial_distance_km"] <= radius_km) & (subset["time_rel_days"].abs() <= tdays)]
    if mag_thr is not None:
        subset = subset[subset["mag"] >= mag_thr]
    pre = subset[subset["time_rel_days"] < 0]
    post = subset[subset["time_rel_days"] > 0]
    pre_rate = len(pre) / tdays if tdays > 0 else np.nan
    post_rate = len(post) / tdays if tdays > 0 else np.nan
    ratio = post_rate / pre_rate if pre_rate and pre_rate > 0 else np.nan
    return {"n_total": int(len(subset)), "n_pre": int(len(pre)), "n_post": int(len(post)), "pre_rate": float(pre_rate), "post_rate": float(post_rate), "rate_ratio": float(ratio)}


def control_compare_for_mainshock(cat: pd.DataFrame, mainshock_row: pd.Series, rng: np.random.Generator) -> Tuple[pd.DataFrame, pd.DataFrame]:
    baseline_rates = []
    random_rates = []
    cat_min, cat_max = cat["datetime"].min(), cat["datetime"].max()
    control_times = make_control_window_times(mainshock_row["matched_datetime"], cat_min, cat_max, rng)
    for mag_thr in CONTROL_MAG_THRESHOLDS:
        for tdays in CONTROL_TIME_WINDOWS:
            observed = compute_rate(cat, tdays, CONTROL_RADIUS_KM, mag_thr, mainshock_row)
            baseline_rates.append({"mainshock": mainshock_row["label"], "control_type": "observed", "mag_threshold": mag_thr if mag_thr is not None else np.nan, "time_window_days": tdays, "radius_km": CONTROL_RADIUS_KM, **observed})
            for ct_idx, ctime in enumerate(control_times):
                ctrl_row = mainshock_row.copy()
                ctrl_row["matched_datetime"] = ctime
                ctrl = compute_rate(cat, tdays, CONTROL_RADIUS_KM, mag_thr, ctrl_row)
                random_rates.append({"mainshock": mainshock_row["label"], "control_type": f"shifted_{ct_idx+1}", "control_time": ctime, "mag_threshold": mag_thr if mag_thr is not None else np.nan, "time_window_days": tdays, "radius_km": CONTROL_RADIUS_KM, **ctrl})
    obs_df = pd.DataFrame(baseline_rates)
    rand_df = pd.DataFrame(random_rates)
    return obs_df, rand_df


def paired_ratio(obs: pd.DataFrame, rand: pd.DataFrame) -> pd.DataFrame:
    if obs.empty or rand.empty:
        return pd.DataFrame()
    rows = []
    for _, o in obs.iterrows():
        o_mag = np.nan if pd.isna(o["mag_threshold"]) else float(o["mag_threshold"])
        rr = rand[(rand["mainshock"] == o["mainshock"]) & (rand["time_window_days"] == o["time_window_days"])]
        if pd.isna(o_mag):
            rr = rr[rr["mag_threshold"].isna()]
        else:
            rr = rr[np.isclose(rr["mag_threshold"].astype(float), o_mag, rtol=0.0, atol=1e-9)]
        if rr.empty:
            continue
        rows.append({
            "mainshock": o["mainshock"],
            "mag_threshold": o["mag_threshold"],
            "time_window_days": o["time_window_days"],
            "observed_rate": o["post_rate"],
            "observed_pre_rate": o["pre_rate"],
            "observed_ratio": o["rate_ratio"],
            "random_rate_median": rr["post_rate"].median(),
            "random_rate_mean": rr["post_rate"].mean(),
            "random_ratio_median": rr["rate_ratio"].median(),
            "excess_rate": o["post_rate"] - rr["post_rate"].median(),
        })
    return pd.DataFrame(rows)


def plot_control_panels(control_summary: pd.DataFrame, title: str, outpath: Path) -> None:
    if control_summary.empty:
        return
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), dpi=200)
    for mainshock, sub in control_summary.groupby("mainshock"):
        x = sub["time_window_days"]
        ax.plot(x, sub["observed_ratio"], marker="o", lw=2, label=f"{mainshock} observed")
        ax.plot(x, sub["random_ratio_median"], marker="s", lw=1.8, linestyle="--", label=f"{mainshock} randomized median")
    ax.set_xlabel("Window length (days)")
    ax.set_ylabel("Post / pre rate ratio")
    ax.set_title(title)
    ax.set_yscale("log")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_background_vs_observed(obs: pd.DataFrame, rand: pd.DataFrame, outpath: Path) -> None:
    if obs.empty or rand.empty:
        return
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), dpi=200, sharey=True)
    for ax, mainshock in zip(axes, sorted(obs["mainshock"].unique())):
        o = obs[obs["mainshock"] == mainshock]
        r = rand[rand["mainshock"] == mainshock]
        ax.scatter(o["time_window_days"], o["post_rate"], c="crimson", s=28, label="observed")
        ax.scatter(r["time_window_days"], r["post_rate"], c="steelblue", s=12, alpha=0.5, label="randomized")
        ax.set_title(mainshock)
        ax.set_xlabel("Window (days)")
        ax.grid(True, alpha=0.2)
    axes[0].set_ylabel("Post-event rate (events/day)")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    try:
        clean_output_dir()
        rng = np.random.default_rng(RANDOM_SEED)
        cat, main, match, seq, summary, window, radial, depth, mag, mecha, station, robustness = load_inputs()
        required = ["datetime", "lat", "lon", "dep", "mag"]
        if not set(required).issubset(cat.columns):
            raise RuntimeError(f"Catalog missing required fields: {sorted(set(required) - set(cat.columns))}")
        if not {"label", "matched_datetime", "matched_lat", "matched_lon", "matched_dep", "matched_mag"}.issubset(match.columns):
            raise RuntimeError("Matched mainshock table missing required fields")
        if seq.empty:
            raise RuntimeError("Sequence table is empty; run step 02 first")
        seq["datetime"] = parse_time(seq["datetime"])
        main = main.copy()
        main["datetime"] = parse_time(main["datetime"])
        match = match.copy()
        match["matched_datetime"] = parse_time(match["matched_datetime"])

        verification = {
            "catalog_rows": int(len(cat)),
            "mainshock_rows": int(len(main)),
            "matched_rows": int(len(match)),
            "sequence_rows": int(len(seq)),
            "summary_rows": int(len(summary)),
            "window_rows": int(len(window)),
            "radial_rows": int(len(radial)),
            "depth_rows": int(len(depth)),
            "mag_rows": int(len(mag)),
            "mechanism_rows": int(len(mecha)),
            "station_rows": int(len(station)),
            "robustness_rows": int(len(robustness)),
        }
        with open(OUTPUT_DIR / "input_inventory.json", "w", encoding="utf-8") as f:
            json.dump(verification, f, indent=2, default=lambda x: x if isinstance(x, (str, int, float, bool)) else None)

        # Baseline and control comparisons
        obs_all = []
        rand_all = []
        control_rows = []
        control_summaries = []
        for _, msh in match.iterrows():
            obs_df, rand_df = control_compare_for_mainshock(cat, msh, rng)
            obs_all.append(obs_df)
            rand_all.append(rand_df)
            comp = paired_ratio(obs_df, rand_df)
            if not comp.empty:
                comp["matched_datetime"] = msh["matched_datetime"]
                control_summaries.append(comp)
            for tdays in CONTROL_TIME_WINDOWS:
                for mag_thr in CONTROL_MAG_THRESHOLDS:
                    b = compute_rate(cat, tdays, CONTROL_RADIUS_KM, mag_thr, msh)
                    control_rows.append({"mainshock": msh["label"], "control_type": "observed_baseline", "time_window_days": tdays, "radius_km": CONTROL_RADIUS_KM, "mag_threshold": mag_thr if mag_thr is not None else np.nan, **b})
                    bg_row = msh.copy()
                    bg_row["matched_datetime"] = msh["matched_datetime"] + pd.Timedelta(days=CONTROL_SHIFT_DAYS)
                    bg = compute_rate(cat, tdays, CONTROL_RADIUS_KM, mag_thr, bg_row)
                    control_rows.append({"mainshock": msh["label"], "control_type": "shifted_background", "time_window_days": tdays, "radius_km": CONTROL_RADIUS_KM, "mag_threshold": mag_thr if mag_thr is not None else np.nan, **bg})
        obs_df = pd.concat(obs_all, ignore_index=True) if obs_all else pd.DataFrame()
        rand_df = pd.concat(rand_all, ignore_index=True) if rand_all else pd.DataFrame()
        comp_df = pd.concat(control_summaries, ignore_index=True) if control_summaries else pd.DataFrame()
        background_df = pd.DataFrame(control_rows)

        if not obs_df.empty:
            obs_df.to_csv(OUTPUT_DIR / "control_observed_rates.csv", index=False)
        if not rand_df.empty:
            rand_df.to_csv(OUTPUT_DIR / "control_randomized_rates.csv", index=False)
        if not comp_df.empty:
            comp_df.to_csv(OUTPUT_DIR / "control_observed_vs_randomized_summary.csv", index=False)
        if not background_df.empty:
            background_df.to_csv(OUTPUT_DIR / "control_background_comparison.csv", index=False)

        # Summary metrics by mainshock
        metrics = []
        for mainshock in sorted(match["label"].unique()):
            sub = summary[summary["mainshock"] == mainshock].copy()
            if sub.empty:
                continue
            baseline = pick_baseline(summary, mainshock)
            obs = comp_df[comp_df["mainshock"] == mainshock] if not comp_df.empty else pd.DataFrame()
            metrics.append({
                "mainshock": mainshock,
                "baseline_radius_km": float(baseline["radius_km"]),
                "baseline_time_window_days": float(baseline["time_window_days"]),
                "baseline_mag_threshold": baseline["mag_threshold"] if pd.notna(baseline.get("mag_threshold", np.nan)) else np.nan,
                "baseline_n_total": int(baseline["n_total"]),
                "baseline_pre_rate": float(baseline["pre_rate"]),
                "baseline_post_rate": float(baseline["post_rate"]),
                "baseline_rate_ratio": float(baseline["rate_ratio"]),
                "baseline_omori_ok": bool(baseline.get("post_omori_fit_ok", False)),
                "baseline_omori_p": float(baseline.get("post_omori_p", np.nan)),
                "baseline_moving_rate_max": float(baseline.get("moving_rate_max", np.nan)),
                "randomized_post_rate_median": float(obs["random_rate_median"].median()) if not obs.empty else np.nan,
                "randomized_rate_ratio_median": float(obs["random_ratio_median"].median()) if not obs.empty else np.nan,
                "observed_minus_randomized_rate": float((obs["observed_rate"] - obs["random_rate_median"]).median()) if not obs.empty else np.nan,
                "robust_radius_count": int((robustness[(robustness["mainshock"] == mainshock) & (robustness["feature"].eq("rate_ratio"))]["stable_across_radius"] == True).sum()) if not robustness.empty and "feature" in robustness.columns and "stable_across_radius" in robustness.columns else np.nan,
            })
        metrics_df = pd.DataFrame(metrics)
        metrics_df.to_csv(OUTPUT_DIR / "control_summary.csv", index=False)

        # Robustness features extracted from step 04 where possible
        robust_features = []
        if not robustness.empty:
            for mainshock, sub in robustness.groupby("mainshock"):
                for feature in ["rate_ratio", "pre_rate", "post_rate", "n_total", "moving_rate_max"]:
                    feat = sub[sub["feature"] == feature]
                    if feat.empty:
                        continue
                    robust_features.append({
                        "mainshock": mainshock,
                        "feature": feature,
                        "stable_across_radius": bool(feat["stable_across_radius"].any()) if "stable_across_radius" in feat.columns else False,
                        "stable_across_time": bool(feat["stable_across_time"].any()) if "stable_across_time" in feat.columns else False,
                        "stable_across_mag": bool(feat["stable_across_mag"].any()) if "stable_across_mag" in feat.columns else False,
                    })
        robust_df = pd.DataFrame(robust_features)
        if not robust_df.empty:
            robust_df.to_csv(OUTPUT_DIR / "robustness_bridge_summary.csv", index=False)

        # simple significance-style comparisons from observed vs randomized controls
        if not comp_df.empty:
            sig = comp_df.groupby(["mainshock", "mag_threshold", "time_window_days"], dropna=False).agg(
                observed_ratio_median=("observed_ratio", "median"),
                randomized_ratio_median=("random_ratio_median", "median"),
                observed_rate_median=("observed_rate", "median"),
                randomized_rate_median=("random_rate_median", "median"),
            ).reset_index()
            sig["ratio_excess"] = sig["observed_ratio_median"] / sig["randomized_ratio_median"]
            sig.to_csv(OUTPUT_DIR / "control_significance_summary.csv", index=False)

        # Figures
        if not comp_df.empty:
            plot_control_panels(comp_df, "Observed vs randomized post/pre rate ratio", OUTPUT_DIR / "figures" / "control_rate_ratio_comparison.png")
        if not rand_df.empty:
            plot_background_vs_observed(obs_df, rand_df, OUTPUT_DIR / "figures" / "observed_vs_randomized_post_rates.png")

        # figure-data tables for reuse
        obs_df.to_csv(OUTPUT_DIR / "figure_data" / "observed_control_rates.csv", index=False)
        rand_df.to_csv(OUTPUT_DIR / "figure_data" / "randomized_control_rates.csv", index=False)
        comp_df.to_csv(OUTPUT_DIR / "figure_data" / "observed_vs_randomized_control_summary.csv", index=False)
        background_df.to_csv(OUTPUT_DIR / "figure_data" / "background_control_rates.csv", index=False)
        metrics_df.to_csv(OUTPUT_DIR / "figure_data" / "control_metrics_summary.csv", index=False)

        manifest = {
            "status": "success",
            "output_dir": str(OUTPUT_DIR),
            "files": sorted([p.name for p in OUTPUT_DIR.glob("**/*") if p.is_file()]),
        }
        with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, default=lambda x: x if isinstance(x, (str, int, float, bool)) else None)
        log("[done] control comparison complete")
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
