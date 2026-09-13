from __future__ import annotations

import json
import math
import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
STEP2_OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis"
)

SUMMARY_CSV = STEP2_OUTPUT_DIR / "sequence_diagnostics_metrics.csv"
COMPARISON_CSV = STEP2_OUTPUT_DIR / "three_sequence_comparison.csv"
CONTROL_CSV = STEP2_OUTPUT_DIR / "control_summary.csv"
ROBUSTNESS_INPUT_CSV = STEP2_OUTPUT_DIR / "robustness_summary.csv"
WINDOW_RATES_CSV = STEP2_OUTPUT_DIR / "time_binned_rates.csv"
MAG_DIST_CSV = STEP2_OUTPUT_DIR / "magnitude_distribution_summary.csv"
DEPTH_DIST_CSV = STEP2_OUTPUT_DIR / "depth_distribution_summary.csv"
RADIAL_DIST_CSV = STEP2_OUTPUT_DIR / "radial_distance_summary.csv"
META_DIR = STEP2_OUTPUT_DIR / "figure_data"
VERIFICATION_JSON = STEP2_OUTPUT_DIR / "sequence_diagnostics_verification.json"

ROBUSTNESS_CSV = OUTPUT_DIR / "robustness_results.csv"
SENSITIVITY_CSV = OUTPUT_DIR / "sensitivity_summary.csv"
STABILITY_CSV = OUTPUT_DIR / "stability_flags.csv"
COMPARISON_OUT_CSV = OUTPUT_DIR / "three_sequence_comparison_baseline.csv"
CONTROL_OUT_CSV = OUTPUT_DIR / "control_comparison_baseline.csv"
GRID_SUMMARY_CSV = OUTPUT_DIR / "parameter_grid_summary.csv"
FIGURE_DATA_DIR = OUTPUT_DIR / "figure_data"

RADIUS_FOCUS = 50.0
TIME_FOCUS_DAYS = 90.0
BASE_DEPTH_STRATEGY = "all"
BASE_MAG_THRESHOLD = np.nan
BASE_METRICS = ["n_total", "n_pre", "n_post", "pre_rate", "post_rate", "rate_ratio", "moving_rate_max", "moving_rate_median", "post_omori_p", "post_omori_r2", "radial_iqr_km", "depth_iqr_km"]
ROBUSTNESS_METRICS = ["rate_ratio", "moving_rate_max", "post_omori_p", "radial_iqr_km", "depth_iqr_km"]


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
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    for p in OUTPUT_DIR.glob("*"):
        if p.is_dir():
            shutil.rmtree(p)
            removed += 1
        else:
            p.unlink()
            removed += 1
    log(f"[0] Cleaned {removed} stale artifacts in {OUTPUT_DIR}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return pd.read_csv(path)


def parse_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def safe_float(x):
    return float(x) if pd.notna(x) else np.nan


def normalize_mag_threshold(value):
    return np.nan if pd.isna(value) else float(value)


def filter_baseline(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["mag_threshold"] = pd.to_numeric(out["mag_threshold"], errors="coerce")
    mask = (
        (out["radius_km"] == RADIUS_FOCUS)
        & (out["time_window_days"] == TIME_FOCUS_DAYS)
        & (out["depth_strategy"] == BASE_DEPTH_STRATEGY)
        & (out["mag_threshold"].isna())
    )
    return out.loc[mask].copy()


def load_inputs():
    summary = read_csv(SUMMARY_CSV)
    comparison = read_csv(COMPARISON_CSV)
    control = read_csv(CONTROL_CSV)
    robustness_input = read_csv(ROBUSTNESS_INPUT_CSV)
    rates = read_csv(WINDOW_RATES_CSV)
    mag_dist = read_csv(MAG_DIST_CSV)
    depth_dist = read_csv(DEPTH_DIST_CSV)
    radial_dist = read_csv(RADIAL_DIST_CSV)
    meta_files = sorted(META_DIR.glob("*_event_centered_subset.csv"))
    verification = json.loads(VERIFICATION_JSON.read_text()) if VERIFICATION_JSON.exists() else {}
    for df in [summary, comparison, control, robustness_input, rates, mag_dist, depth_dist, radial_dist]:
        if "mag_threshold" in df.columns:
            df["mag_threshold"] = pd.to_numeric(df["mag_threshold"], errors="coerce")
    if summary.empty:
        raise RuntimeError("sequence diagnostics summary is empty; previous task outputs are missing or incomplete")
    if not meta_files:
        log("[1] Warning: no figure-data subset files found in previous task outputs")
    return summary, comparison, control, robustness_input, rates, mag_dist, depth_dist, radial_dist, meta_files, verification


def summarize_grid(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mainshock, sdf in summary.groupby("mainshock"):
        for radius in sorted(sdf["radius_km"].dropna().unique()):
            for tdays in sorted(sdf["time_window_days"].dropna().unique()):
                for depth_strategy in sorted(sdf["depth_strategy"].dropna().unique()):
                    for mag_threshold in sorted(sdf["mag_threshold"].dropna().unique().tolist() + [np.nan], key=lambda x: (pd.isna(x), x if pd.notna(x) else -999.0)):
                        sub = sdf[(sdf["radius_km"] == radius) & (sdf["time_window_days"] == tdays) & (sdf["depth_strategy"] == depth_strategy)]
                        if pd.isna(mag_threshold):
                            sub = sub[sub["mag_threshold"].isna()]
                        else:
                            sub = sub[sub["mag_threshold"] == mag_threshold]
                        if sub.empty:
                            continue
                        row = sub.iloc[0]
                        rows.append({
                            "mainshock": mainshock,
                            "radius_km": float(radius),
                            "time_window_days": float(tdays),
                            "depth_strategy": depth_strategy,
                            "mag_threshold": np.nan if pd.isna(mag_threshold) else float(mag_threshold),
                            "n_total": int(row["n_total"]),
                            "n_post": int(row["n_post"]),
                            "rate_ratio": safe_float(row["rate_ratio"]),
                            "moving_rate_max": safe_float(row["moving_rate_max"]),
                            "post_omori_p": safe_float(row["post_omori_p"]),
                            "radial_iqr_km": safe_float(row["radial_iqr_km"]),
                            "depth_iqr_km": safe_float(row["depth_iqr_km"]),
                            "sparse_flag": bool(row["n_total"] < 15 or row["n_post"] < 5),
                        })
    return pd.DataFrame(rows)


def stability_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mainshock, sdf in summary.groupby("mainshock"):
        base = filter_baseline(sdf)
        if base.empty:
            base = sdf.iloc[[0]]
        base = base.iloc[0]
        for metric in ROBUSTNESS_METRICS:
            vals = pd.to_numeric(sdf[metric], errors="coerce").dropna()
            if vals.empty:
                continue
            base_val = float(base[metric]) if pd.notna(base[metric]) else np.nan
            rows.append({
                "mainshock": mainshock,
                "metric": metric,
                "baseline_value": base_val,
                "median_value": float(vals.median()),
                "mean_value": float(vals.mean()),
                "iqr_value": float(vals.quantile(0.75) - vals.quantile(0.25)),
                "cv_value": float(vals.std(ddof=0) / vals.mean()) if vals.mean() != 0 else np.nan,
                "min_value": float(vals.min()),
                "max_value": float(vals.max()),
                "sign_consistency_fraction": float((np.sign(vals) == np.sign(base_val)).mean()) if pd.notna(base_val) and base_val != 0 else np.nan,
                "n_windows": int(len(vals)),
            })
    return pd.DataFrame(rows)


def feature_stability_flags(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mainshock, sdf in summary.groupby("mainshock"):
        base = filter_baseline(sdf)
        if base.empty:
            base = sdf.iloc[[0]]
        base = base.iloc[0]
        features = ["rate_ratio", "moving_rate_max", "radial_iqr_km", "depth_iqr_km", "post_omori_p"]
        for feature in features:
            vals = pd.to_numeric(sdf[feature], errors="coerce").dropna()
            if vals.empty:
                continue
            if feature in ["rate_ratio", "moving_rate_max"]:
                robust = float((vals > 1.0).mean()) if feature == "rate_ratio" else float(vals.notna().mean())
            elif feature == "post_omori_p":
                robust = float(((vals >= 0.5) & (vals <= 2.5)).mean())
            else:
                q = float(base[feature]) if pd.notna(base[feature]) else np.nan
                robust = float((np.abs(vals - q) <= max(1.0, 0.25 * abs(q) if pd.notna(q) and q != 0 else 1.0)).mean()) if pd.notna(q) else np.nan
            rows.append({
                "mainshock": mainshock,
                "feature": feature,
                "baseline_value": safe_float(base[feature]) if feature in base.index else np.nan,
                "robust_fraction": robust,
                "n_windows": int(len(vals)),
                "sparse_reference": bool(base["n_total"] < 15 or base["n_post"] < 5),
            })
    return pd.DataFrame(rows)


def compare_three_sequences(summary: pd.DataFrame) -> pd.DataFrame:
    base = filter_baseline(summary)
    if base.empty:
        base = summary.copy()
    rows = []
    for mainshock, sdf in base.groupby("mainshock"):
        row = sdf.iloc[0].to_dict()
        rows.append({
            "mainshock": mainshock,
            "n_total": int(row["n_total"]),
            "n_pre": int(row["n_pre"]),
            "n_post": int(row["n_post"]),
            "pre_rate": safe_float(row["pre_rate"]),
            "post_rate": safe_float(row["post_rate"]),
            "rate_ratio": safe_float(row["rate_ratio"]),
            "pre_post_balance": safe_float(row.get("pre_post_balance", np.nan)),
            "moving_rate_max": safe_float(row["moving_rate_max"]),
            "moving_rate_median": safe_float(row["moving_rate_median"]),
            "burstiness_index": safe_float(row["moving_rate_max"] / row["moving_rate_median"] if pd.notna(row["moving_rate_median"]) and row["moving_rate_median"] > 0 else np.nan),
            "post_omori_p": safe_float(row["post_omori_p"]),
            "post_omori_r2": safe_float(row["post_omori_r2"]),
            "radial_q50_km": safe_float(row["radial_q50_km"]),
            "depth_q50_km": safe_float(row["depth_q50_km"]),
            "mag_q50": safe_float(row["mag_q50"]),
            "mecha_overlap_count": int(row.get("mecha_overlap_count", 0)) if pd.notna(row.get("mecha_overlap_count", 0)) else 0,
            "stations_within_100km": int(row.get("stations_within_100km", 0)) if pd.notna(row.get("stations_within_100km", 0)) else 0,
        })
    return pd.DataFrame(rows)


def control_baseline(control: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    base = filter_baseline(summary)
    if base.empty:
        base = summary.copy()
    rows = []
    for _, crow in control.iterrows():
        ref = base[base["mainshock"] == crow["mainshock"]]
        if ref.empty:
            ref = summary[summary["mainshock"] == crow["mainshock"]].iloc[[0]]
        ref = ref.iloc[0]
        rows.append({
            "mainshock": crow["mainshock"],
            "control_window_start": crow.get("control_window_start", np.nan),
            "control_window_end": crow.get("control_window_end", np.nan),
            "control_rate_per_day": safe_float(crow.get("control_rate_per_day", np.nan)),
            "control_n_total": int(crow.get("control_n_total", np.nan)) if pd.notna(crow.get("control_n_total", np.nan)) else np.nan,
            "baseline_n_total": int(ref["n_total"]),
            "baseline_pre_rate": safe_float(ref["pre_rate"]),
            "baseline_post_rate": safe_float(ref["post_rate"]),
            "baseline_rate_ratio": safe_float(ref["rate_ratio"]),
            "relative_control_rate": safe_float(crow.get("control_rate_per_day", np.nan) / ref["pre_rate"] if pd.notna(ref["pre_rate"]) and ref["pre_rate"] > 0 else np.nan),
        })
    return pd.DataFrame(rows)


def save_fig_data(summary: pd.DataFrame, comparison: pd.DataFrame, control: pd.DataFrame, grid: pd.DataFrame, stability: pd.DataFrame) -> None:
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(FIGURE_DATA_DIR / "summary_baseline_grid.csv", index=False)
    comparison.to_csv(FIGURE_DATA_DIR / "comparison_baseline.csv", index=False)
    control.to_csv(FIGURE_DATA_DIR / "control_baseline.csv", index=False)
    grid.to_csv(FIGURE_DATA_DIR / "parameter_grid_summary.csv", index=False)
    stability.to_csv(FIGURE_DATA_DIR / "stability_flags.csv", index=False)


def main() -> None:
    clean_output_dir()
    log("[1] Loading diagnostics outputs")
    summary, comparison, control, robustness_input, rates, mag_dist, depth_dist, radial_dist, meta_files, verification = load_inputs()
    required = ["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "n_total", "n_pre", "n_post", "pre_rate", "post_rate", "rate_ratio", "moving_rate_max", "moving_rate_median", "post_omori_p", "post_omori_r2"]
    missing = [c for c in required if c not in summary.columns]
    if missing:
        raise RuntimeError(f"sequence diagnostics summary missing required columns: {missing}")
    for derived_col in ["radial_iqr_km", "depth_iqr_km"]:
        if derived_col not in summary.columns:
            summary[derived_col] = np.nan
    for name, df in [("comparison", comparison), ("control", control), ("robustness_input", robustness_input), ("rates", rates), ("mag_dist", mag_dist), ("depth_dist", depth_dist), ("radial_dist", radial_dist)]:
        if df.empty:
            raise RuntimeError(f"{name} input from previous task is empty; rerun Task 03 before Task 04")
    summary = summary.copy()
    summary["mag_threshold"] = pd.to_numeric(summary["mag_threshold"], errors="coerce")
    control = control.copy() if not control.empty else pd.DataFrame(columns=["mainshock"])

    log("[2] Building parameter-grid robustness table")
    grid = summarize_grid(summary)
    grid.to_csv(GRID_SUMMARY_CSV, index=False)

    log("[3] Computing stability metrics")
    stability = stability_summary(summary)
    stability.to_csv(STABILITY_CSV, index=False)
    flags = feature_stability_flags(summary)
    flags.to_csv(OUTPUT_DIR / "stability_feature_flags.csv", index=False)

    log("[4] Comparing the three mainshock sequences on the baseline grid")
    comparison_base = compare_three_sequences(summary)
    comparison_base.to_csv(COMPARISON_OUT_CSV, index=False)

    log("[5] Summarizing control comparison against baseline sequence windows")
    control_base = control_baseline(control, summary)
    control_base.to_csv(CONTROL_OUT_CSV, index=False)

    log("[6] Writing combined robustness results")
    robustness_rows = []
    baseline = filter_baseline(summary)
    if baseline.empty:
        baseline = summary.iloc[[0]]
    baseline_map = {row["mainshock"]: row for _, row in baseline.iterrows()}
    for _, row in summary.iterrows():
        base = baseline_map.get(row["mainshock"], baseline.iloc[0])
        robustness_rows.append({
            "mainshock": row["mainshock"],
            "radius_km": float(row["radius_km"]),
            "time_window_days": float(row["time_window_days"]),
            "depth_strategy": row["depth_strategy"],
            "mag_threshold": np.nan if pd.isna(row["mag_threshold"]) else float(row["mag_threshold"]),
            "n_total": int(row["n_total"]),
            "n_post": int(row["n_post"]),
            "rate_ratio": safe_float(row["rate_ratio"]),
            "moving_rate_max": safe_float(row["moving_rate_max"]),
            "post_omori_p": safe_float(row["post_omori_p"]),
            "radial_iqr_km": safe_float(row.get("radial_iqr_km", np.nan)),
            "depth_iqr_km": safe_float(row.get("depth_iqr_km", np.nan)),
            "baseline_rate_ratio": safe_float(base["rate_ratio"]),
            "baseline_moving_rate_max": safe_float(base["moving_rate_max"]),
            "baseline_post_omori_p": safe_float(base["post_omori_p"]),
            "rate_ratio_delta": safe_float(row["rate_ratio"] - base["rate_ratio"] if pd.notna(row["rate_ratio"]) and pd.notna(base["rate_ratio"]) else np.nan),
            "sparse_flag": bool(row["n_total"] < 15 or row["n_post"] < 5),
        })
    robustness = pd.DataFrame(robustness_rows)
    robustness.to_csv(ROBUSTNESS_CSV, index=False)

    save_fig_data(summary, comparison_base, control_base, grid, stability)

    control_out = control_base.copy()
    control_out.to_csv(CONTROL_OUT_CSV, index=False)
    comparison_base.to_csv(COMPARISON_OUT_CSV, index=False)
    stability.to_csv(STABILITY_CSV, index=False)

    sensitivity_rows = []
    for mainshock, sdf in summary.groupby("mainshock"):
        for param in ["radius_km", "time_window_days", "depth_strategy", "mag_threshold"]:
            vals = sdf[param].dropna().unique()
            sensitivity_rows.append({
                "mainshock": mainshock,
                "parameter": param,
                "n_levels": int(len(vals)),
                "baseline_level": safe_float(filter_baseline(sdf)[param].iloc[0]) if not filter_baseline(sdf).empty and pd.api.types.is_numeric_dtype(sdf[param]) else (filter_baseline(sdf)[param].iloc[0] if not filter_baseline(sdf).empty else np.nan),
                "stable_rate_ratio_fraction": float((pd.to_numeric(sdf["rate_ratio"], errors="coerce") > 1.0).mean()),
                "stable_post_omori_fraction": float(((pd.to_numeric(sdf["post_omori_p"], errors="coerce") >= 0.5) & (pd.to_numeric(sdf["post_omori_p"], errors="coerce") <= 2.5)).mean()),
                "n_windows": int(len(sdf)),
            })
    pd.DataFrame(sensitivity_rows).to_csv(SENSITIVITY_CSV, index=False)

    verification_out = {
        "source_verification": verification,
        "n_summary_rows": int(len(summary)),
        "n_robustness_rows": int(len(robustness)),
        "n_grid_rows": int(len(grid)),
        "n_stability_rows": int(len(stability)),
        "n_feature_flags_rows": int(len(flags)),
        "n_control_rows": int(len(control_base)),
        "mainshock_summary": comparison_base.to_dict(orient="records"),
        "robust_features": ROBUSTNESS_METRICS,
        "baseline_definition": {
            "radius_km": RADIUS_FOCUS,
            "time_window_days": TIME_FOCUS_DAYS,
            "depth_strategy": BASE_DEPTH_STRATEGY,
            "mag_threshold": None,
        },
    }
    (OUTPUT_DIR / "robustness_verification.json").write_text(json.dumps(verification_out, indent=2, default=to_jsonable), encoding="utf-8")

    log(f"[7] Saved robustness table to {ROBUSTNESS_CSV}")
    log(f"[7] Saved stability summary to {STABILITY_CSV}")
    log(f"[7] Saved feature flags to {OUTPUT_DIR / 'stability_feature_flags.csv'}")
    log(f"[7] Saved baseline three-sequence comparison to {COMPARISON_OUT_CSV}")
    log(f"[7] Saved control comparison to {CONTROL_OUT_CSV}")
    log(f"[7] Saved parameter grid summary to {GRID_SUMMARY_CSV}")
    log("[8] Baseline three-sequence comparison preview:")
    log(comparison_base.to_string(index=False))
    log("[9] Robustness analysis completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
