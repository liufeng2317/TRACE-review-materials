from __future__ import annotations

import json
import math
import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
STEP2_OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics"
)

SEQ_PATH = STEP2_OUTPUT_DIR / "event_centered_sequence_table.csv"
SUMMARY_PATH = STEP2_OUTPUT_DIR / "sequence_diagnostics_summary.csv"
COUNTS_PATH = STEP2_OUTPUT_DIR / "sequence_extraction_counts.csv"
CONTROL_PATH = STEP2_OUTPUT_DIR / "sequence_control_comparison.csv"
META_PATH = STEP2_OUTPUT_DIR / "mainshock_sequence_metadata.csv"
VERIFICATION_PATH = STEP2_OUTPUT_DIR / "sequence_extraction_verification.json"
MECHA_PATH = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_PATH = BASE_DIR / "stations/station.sta"
CATALOG_PATH = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MAIN_PATH = BASE_DIR / "catalog/main_earthquake.csv"

SUMMARY_CSV = OUTPUT_DIR / "sequence_diagnostics_metrics.csv"
WINDOW_CSV = OUTPUT_DIR / "time_binned_rates.csv"
RADIAL_CSV = OUTPUT_DIR / "radial_distance_summary.csv"
DEPTH_CSV = OUTPUT_DIR / "depth_distribution_summary.csv"
MAG_CSV = OUTPUT_DIR / "magnitude_distribution_summary.csv"
MECHA_CSV = OUTPUT_DIR / "mechanism_overlap_summary.csv"
ROBUSTNESS_CSV = OUTPUT_DIR / "robustness_summary.csv"
COMPARISON_CSV = OUTPUT_DIR / "three_sequence_comparison.csv"
CONTROL_SUMMARY_CSV = OUTPUT_DIR / "control_summary.csv"
FIG_DATA_DIR = OUTPUT_DIR / "figure_data"

RADIUS_FOCUS = 50.0
TIME_FOCUS_DAYS = 90.0
MAG_THRESHOLDS = [None, 1.2, 1.5, 2.0, 2.5]
MOVING_WINDOW_DAYS = 7.0
RATE_BIN_DAYS = 1.0
OMORI_MIN_POST_EVENTS = 12
OMORI_MIN_SPAN_DAYS = 14.0
OMORI_BINS = 24
DEPTH_BINS = np.array([0, 10, 20, 30, 40, 50, 80, 120], dtype=float)


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
    FIG_DATA_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    for pattern in ["*.csv", "*.json", "*.txt", "*.png"]:
        for p in OUTPUT_DIR.glob(pattern):
            if p.is_file() or p.is_symlink():
                p.unlink()
                removed += 1
            elif p.is_dir():
                shutil.rmtree(p)
                removed += 1
    for p in FIG_DATA_DIR.glob("*"):
        if p.is_file() or p.is_symlink():
            p.unlink()
            removed += 1
        elif p.is_dir():
            shutil.rmtree(p)
            removed += 1
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
    seq = pd.read_csv(SEQ_PATH)
    summary = pd.read_csv(SUMMARY_PATH)
    counts = pd.read_csv(COUNTS_PATH)
    control = pd.read_csv(CONTROL_PATH)
    meta = pd.read_csv(META_PATH)
    with open(VERIFICATION_PATH, "r", encoding="utf-8") as f:
        verification = json.load(f)
    mecha = pd.read_csv(MECHA_PATH)
    station = pd.read_csv(STATION_PATH, sep=None, engine="python")
    catalog = pd.read_csv(CATALOG_PATH)
    main = pd.read_csv(MAIN_PATH)

    seq["datetime"] = parse_time(seq["datetime"])
    for col in ["matched_datetime"]:
        if col in meta.columns:
            meta[col] = parse_time(meta[col])
    mecha["origin_time"] = parse_time(mecha["origin_time"])
    for df in [catalog, main]:
        if "datetime" in df.columns:
            df["datetime"] = parse_time(df["datetime"])
    return seq, summary, counts, control, meta, verification, mecha, station, catalog, main


def require_columns(df: pd.DataFrame, required: List[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"{name} missing required columns: {missing}")


def mechanism_flag_column(mecha: pd.DataFrame) -> str:
    for candidate in ["quality", "mech_flag", "available", "flag", "status"]:
        if candidate in mecha.columns:
            return candidate
    return ""


def summarize_mecha(seq: pd.DataFrame, mecha: pd.DataFrame, mainshock_row: pd.Series) -> Dict[str, object]:
    if seq.empty or mecha.empty:
        return {"mecha_overlap_count": 0, "mecha_available": False, "mecha_quality_mode": None}
    dt_days = (mecha["origin_time"] - mainshock_row["matched_datetime"]).dt.total_seconds().abs() / 86400.0
    dist_km = haversine_km(
        float(mainshock_row["matched_lat"]),
        float(mainshock_row["matched_lon"]),
        mecha["lat_deg"].to_numpy(),
        mecha["lon_deg"].to_numpy(),
    )
    mask = (dt_days <= 90.0) & (dist_km <= 100.0)
    flag_col = mechanism_flag_column(mecha)
    quality_mode = None
    if flag_col and mask.any():
        vals = mecha.loc[mask, flag_col].astype(str).value_counts()
        quality_mode = vals.index[0]
    return {
        "mecha_overlap_count": int(mask.sum()),
        "mecha_available": bool(mask.any()),
        "mecha_quality_mode": quality_mode,
    }


def summarize_station_coverage(station: pd.DataFrame, mainshock_row: pd.Series) -> Dict[str, object]:
    lat_col = "latitude" if "latitude" in station.columns else "lat" if "lat" in station.columns else None
    lon_col = "longitude" if "longitude" in station.columns else "lon" if "lon" in station.columns else None
    if lat_col is None or lon_col is None:
        return {"station_count": int(len(station)), "stations_within_100km": None, "stations_within_200km": None}
    dist = haversine_km(float(mainshock_row["matched_lat"]), float(mainshock_row["matched_lon"]), station[lat_col].to_numpy(), station[lon_col].to_numpy())
    return {
        "station_count": int(len(station)),
        "stations_within_100km": int(np.sum(dist <= 100.0)),
        "stations_within_200km": int(np.sum(dist <= 200.0)),
    }


def add_window_columns(seq: pd.DataFrame) -> pd.DataFrame:
    out = seq.copy()
    out["pre_post"] = np.where(out["time_rel_days"] < 0, "pre", np.where(out["time_rel_days"] > 0, "post", "at_mainshock"))
    out["abs_time_rel_days"] = out["time_rel_days"].abs()
    out["depth_bin"] = pd.cut(out["dep"], bins=DEPTH_BINS, right=False, include_lowest=True)
    return out


def omori_fit(post_df: pd.DataFrame) -> Dict[str, object]:
    if len(post_df) < OMORI_MIN_POST_EVENTS:
        return {"fit_ok": False, "c": np.nan, "k": np.nan, "p": np.nan, "r2": np.nan, "n_fit": int(len(post_df))}
    t = post_df["time_rel_days"].to_numpy()
    t = t[t > 0]
    if len(t) < OMORI_MIN_POST_EVENTS:
        return {"fit_ok": False, "c": np.nan, "k": np.nan, "p": np.nan, "r2": np.nan, "n_fit": int(len(t))}
    if (t.max() - t.min()) < OMORI_MIN_SPAN_DAYS:
        return {"fit_ok": False, "c": np.nan, "k": np.nan, "p": np.nan, "r2": np.nan, "n_fit": int(len(t))}
    lo = max(0.02, float(np.nanmin(t)))
    hi = float(np.nanmax(t) + 1e-6)
    bins = np.logspace(np.log10(lo), np.log10(hi), OMORI_BINS)
    counts, edges = np.histogram(t, bins=bins)
    mids = np.sqrt(edges[:-1] * edges[1:])
    valid = counts > 0
    if valid.sum() < 4:
        return {"fit_ok": False, "c": np.nan, "k": np.nan, "p": np.nan, "r2": np.nan, "n_fit": int(len(t))}
    x = np.log10(mids[valid])
    y = np.log10(counts[valid] / np.diff(edges)[valid])
    A = np.vstack([np.ones_like(x), -np.log10(mids[valid] + 1e-9)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    intercept, p = coef
    yhat = A @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return {"fit_ok": True, "c": 0.01, "k": float(10**intercept), "p": float(p), "r2": float(r2), "n_fit": int(len(t))}


def count_rate_bins(seq: pd.DataFrame, bin_days: float) -> pd.DataFrame:
    if seq.empty:
        return pd.DataFrame(columns=["time_bin_start_days", "time_bin_end_days", "count", "rate_per_day", "pre_post"])
    lo = math.floor(seq["time_rel_days"].min() / bin_days) * bin_days
    hi = math.ceil(seq["time_rel_days"].max() / bin_days) * bin_days
    edges = np.arange(lo, hi + bin_days, bin_days)
    if len(edges) < 2:
        edges = np.array([lo, lo + bin_days])
    cats = pd.cut(seq["time_rel_days"], bins=edges, right=False, include_lowest=True)
    grouped = seq.groupby(cats, observed=True).size().reset_index(name="count")
    grouped["time_bin_start_days"] = grouped["time_rel_days"].apply(lambda x: float(x.left))
    grouped["time_bin_end_days"] = grouped["time_rel_days"].apply(lambda x: float(x.right))
    grouped["rate_per_day"] = grouped["count"] / bin_days
    grouped["pre_post"] = np.where(
        grouped["time_bin_end_days"].to_numpy(dtype=float) <= 0,
        "pre",
        np.where(grouped["time_bin_start_days"].to_numpy(dtype=float) >= 0, "post", "crosses_mainshock"),
    )
    return grouped[["time_bin_start_days", "time_bin_end_days", "count", "rate_per_day", "pre_post"]]


def summarize_distributions(seq: pd.DataFrame, mainshock: str, radius: float, tdays: float, depth_strategy: str, mag_threshold) -> Dict[str, Dict[str, object]]:
    out = {}
    if seq.empty:
        return out
    bins_mag = np.arange(max(0.0, np.floor(seq["mag"].min() * 2) / 2), np.ceil(seq["mag"].max() * 2) / 2 + 0.25, 0.25)
    if len(bins_mag) < 2:
        bins_mag = np.array([seq["mag"].min(), seq["mag"].max() + 0.1])
    mag_hist = np.histogram(seq["mag"], bins=bins_mag)
    depth_hist = np.histogram(seq["dep"], bins=DEPTH_BINS)
    radial_bins = np.arange(0, max(radius, float(seq["radial_distance_km"].max())) + 5.0, 5.0)
    radial_hist = np.histogram(seq["radial_distance_km"], bins=radial_bins)
    for name, hist, edges in [
        ("magnitude", mag_hist, bins_mag),
        ("depth", depth_hist, DEPTH_BINS),
        ("radial", radial_hist, radial_bins),
    ]:
        counts, e = hist
        out[name] = {
            "mainshock": mainshock,
            "radius_km": radius,
            "time_window_days": tdays,
            "depth_strategy": depth_strategy,
            "mag_threshold": np.nan if mag_threshold is None else mag_threshold,
            "bin_left": e[:-1].tolist(),
            "bin_right": e[1:].tolist(),
            "count": counts.astype(int).tolist(),
            "fraction": (counts / counts.sum()).tolist() if counts.sum() > 0 else [np.nan] * len(counts),
        }
    return out


def summarize_sequence(seq: pd.DataFrame, summary_row: pd.Series, mecha: pd.DataFrame, station: pd.DataFrame, mainshock_row: pd.Series) -> Dict[str, object]:
    pre = seq[seq["time_rel_days"] < 0]
    post = seq[seq["time_rel_days"] > 0]
    duration_pre = float(summary_row["duration_pre_days"])
    duration_post = float(summary_row["duration_post_days"])
    pre_rate = float(len(pre) / duration_pre) if duration_pre > 0 else np.nan
    post_rate = float(len(post) / duration_post) if duration_post > 0 else np.nan
    rate_ratio = float(post_rate / pre_rate) if pre_rate and pre_rate > 0 else np.nan
    moving = count_rate_bins(seq, RATE_BIN_DAYS)
    omori = omori_fit(post)
    mecha_info = summarize_mecha(seq, mecha, mainshock_row)
    station_info = summarize_station_coverage(station, mainshock_row)
    if len(seq):
        radial_q25, radial_q50, radial_q75 = np.nanpercentile(seq["radial_distance_km"], [25, 50, 75])
        depth_q25, depth_q50, depth_q75 = np.nanpercentile(seq["dep"], [25, 50, 75])
        mag_q25, mag_q50, mag_q75 = np.nanpercentile(seq["mag"], [25, 50, 75])
    else:
        radial_q25 = radial_q50 = radial_q75 = np.nan
        depth_q25 = depth_q50 = depth_q75 = np.nan
        mag_q25 = mag_q50 = mag_q75 = np.nan
    spread = float(seq["radial_distance_km"].quantile(0.75) - seq["radial_distance_km"].quantile(0.25)) if len(seq) else np.nan
    depth_spread = float(seq["dep"].quantile(0.75) - seq["dep"].quantile(0.25)) if len(seq) else np.nan
    return {
        "mainshock": summary_row["mainshock"],
        "radius_km": float(summary_row["radius_km"]),
        "time_window_days": float(summary_row["time_window_days"]),
        "depth_strategy": summary_row["depth_strategy"],
        "mag_threshold": summary_row["mag_threshold"],
        "n_total": int(len(seq)),
        "n_pre": int(len(pre)),
        "n_post": int(len(post)),
        "pre_rate": pre_rate,
        "post_rate": post_rate,
        "rate_ratio": rate_ratio,
        "pre_post_balance": float((len(post) - len(pre)) / len(seq)) if len(seq) else np.nan,
        "moving_rate_max": float(moving["rate_per_day"].max()) if len(moving) else np.nan,
        "moving_rate_median": float(moving["rate_per_day"].median()) if len(moving) else np.nan,
        "moving_rate_cv": float(moving["rate_per_day"].std(ddof=0) / moving["rate_per_day"].mean()) if len(moving) and moving["rate_per_day"].mean() > 0 else np.nan,
        "post_omori_c": omori["c"],
        "post_omori_k": omori["k"],
        "post_omori_p": omori["p"],
        "post_omori_r2": omori["r2"],
        "post_omori_fit_ok": omori["fit_ok"],
        "radial_q25_km": float(radial_q25),
        "radial_q50_km": float(radial_q50),
        "radial_q75_km": float(radial_q75),
        "depth_q25_km": float(depth_q25),
        "depth_q50_km": float(depth_q50),
        "depth_q75_km": float(depth_q75),
        "mag_q25": float(mag_q25),
        "mag_q50": float(mag_q50),
        "mag_q75": float(mag_q75),
        "radial_iqr_km": spread,
        "depth_iqr_km": depth_spread,
        "mecha_overlap_count": mecha_info["mecha_overlap_count"],
        "mecha_available": mecha_info["mecha_available"],
        "mecha_quality_mode": mecha_info["mecha_quality_mode"],
        "station_count": station_info["station_count"],
        "stations_within_100km": station_info["stations_within_100km"],
        "stations_within_200km": station_info["stations_within_200km"],
        "pre_post_duration_ratio": float(duration_post / duration_pre) if duration_pre > 0 else np.nan,
    }


def sequence_key(row: pd.Series) -> Tuple:
    return (row["mainshock"], float(row["radius_km"]), float(row["time_window_days"]), row["depth_strategy"], np.nan if pd.isna(row["mag_threshold"]) else float(row["mag_threshold"]))


def build_robustness(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for mainshock, sdf in summary.groupby("mainshock"):
        if sdf.empty:
            continue
        baseline = sdf[(sdf["radius_km"] == RADIUS_FOCUS) & (sdf["time_window_days"] == TIME_FOCUS_DAYS) & (sdf["depth_strategy"] == "all") & (sdf["mag_threshold"].isna())]
        if baseline.empty:
            baseline = sdf.iloc[[0]]
        base = baseline.iloc[0]
        for metric in ["rate_ratio", "moving_rate_max", "post_omori_p", "radial_iqr_km", "depth_iqr_km"]:
            if metric not in sdf.columns:
                continue
            vals = sdf[metric].dropna()
            if len(vals) == 0:
                continue
            rows.append({
                "mainshock": mainshock,
                "metric": metric,
                "baseline_value": float(base[metric]) if metric in base.index and pd.notna(base[metric]) else np.nan,
                "median_value": float(vals.median()),
                "iqr_value": float(vals.quantile(0.75) - vals.quantile(0.25)),
                "cv_value": float(vals.std(ddof=0) / vals.mean()) if vals.mean() != 0 else np.nan,
                "sign_stable_fraction": float((np.sign(vals) == np.sign(base[metric])).mean()) if metric in base.index and pd.notna(base[metric]) and base[metric] != 0 else np.nan,
                "n_windows": int(len(vals)),
            })
    return pd.DataFrame(rows)


def build_three_sequence_comparison(summary: pd.DataFrame) -> pd.DataFrame:
    baseline = summary[(summary["radius_km"] == RADIUS_FOCUS) & (summary["time_window_days"] == TIME_FOCUS_DAYS) & (summary["depth_strategy"] == "all") & (summary["mag_threshold"].isna())].copy()
    if baseline.empty:
        baseline = summary.copy()
    metrics = [
        "n_total",
        "n_pre",
        "n_post",
        "pre_rate",
        "post_rate",
        "rate_ratio",
        "moving_rate_max",
        "moving_rate_median",
        "post_omori_p",
        "post_omori_r2",
        "radial_q50_km",
        "depth_q50_km",
        "mag_q50",
        "mecha_overlap_count",
        "stations_within_100km",
    ]
    rows = []
    for mainshock, g in baseline.groupby("mainshock"):
        row = {"mainshock": mainshock}
        one = g.iloc[0]
        for m in metrics:
            row[m] = one[m] if m in one.index else np.nan
        row["burstiness_index"] = one["moving_rate_max"] / one["moving_rate_median"] if "moving_rate_median" in one.index and one["moving_rate_median"] and one["moving_rate_median"] > 0 else np.nan
        row["pre_post_balance"] = one["pre_post_balance"] if "pre_post_balance" in one.index else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def save_distribution_tables(summary: pd.DataFrame, seq: pd.DataFrame) -> None:
    mag_rows = []
    depth_rows = []
    radial_rows = []
    for _, row in summary.iterrows():
        mask = (
            (seq["mainshock"] == row["mainshock"]) &
            (seq["radius_km"] == row["radius_km"]) &
            (seq["time_window_days"] == row["time_window_days"]) &
            (seq["depth_strategy"] == row["depth_strategy"]) &
            (seq["mag_threshold"].fillna(-9999) == (row["mag_threshold"] if pd.notna(row["mag_threshold"]) else -9999))
        )
        sdf = seq.loc[mask]
        if sdf.empty:
            continue
        mag_edges = np.arange(max(0.0, np.floor(sdf["mag"].min() * 2) / 2), np.ceil(sdf["mag"].max() * 2) / 2 + 0.25, 0.25)
        if len(mag_edges) < 2:
            mag_edges = np.array([sdf["mag"].min(), sdf["mag"].max() + 0.1])
        depth_edges = DEPTH_BINS
        radial_edges = np.arange(0, max(float(row["radius_km"]), float(sdf["radial_distance_km"].max())) + 5.0, 5.0)
        for name, edges, data, store in [
            ("mag", mag_edges, sdf["mag"], mag_rows),
            ("depth", depth_edges, sdf["dep"], depth_rows),
            ("radial", radial_edges, sdf["radial_distance_km"], radial_rows),
        ]:
            counts, _ = np.histogram(data, bins=edges)
            for i in range(len(edges) - 1):
                store.append({
                    "mainshock": row["mainshock"],
                    "radius_km": row["radius_km"],
                    "time_window_days": row["time_window_days"],
                    "depth_strategy": row["depth_strategy"],
                    "mag_threshold": row["mag_threshold"],
                    "distribution": name,
                    "bin_left": float(edges[i]),
                    "bin_right": float(edges[i + 1]),
                    "count": int(counts[i]),
                    "fraction": float(counts[i] / counts.sum()) if counts.sum() > 0 else np.nan,
                })
    pd.DataFrame(mag_rows).to_csv(MAG_CSV, index=False)
    pd.DataFrame(depth_rows).to_csv(DEPTH_CSV, index=False)
    pd.DataFrame(radial_rows).to_csv(RADIAL_CSV, index=False)


def save_window_rates(seq: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, sdf in seq.groupby(["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold"], dropna=False):
        binned = count_rate_bins(sdf, RATE_BIN_DAYS)
        if binned.empty:
            continue
        for _, r in binned.iterrows():
            rows.append({
                "mainshock": key[0],
                "radius_km": key[1],
                "time_window_days": key[2],
                "depth_strategy": key[3],
                "mag_threshold": key[4],
                **r.to_dict(),
            })
    df = pd.DataFrame(rows)
    df.to_csv(WINDOW_CSV, index=False)
    return df


def save_mecha_summary(seq: pd.DataFrame, mecha: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, mr in meta.iterrows():
        for _, row in seq[seq["mainshock"] == mr["mainshock"]].groupby(["radius_km", "time_window_days", "depth_strategy", "mag_threshold"], dropna=False):
            sdf = row
            info = summarize_mecha(sdf, mecha, mr)
            rows.append({"mainshock": mr["mainshock"], "radius_km": sdf["radius_km"].iloc[0], "time_window_days": sdf["time_window_days"].iloc[0], "depth_strategy": sdf["depth_strategy"].iloc[0], "mag_threshold": sdf["mag_threshold"].iloc[0], **info})
    out = pd.DataFrame(rows)
    out.to_csv(MECHA_CSV, index=False)
    return out


def save_control_summary(control: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    base = summary[(summary["radius_km"] == RADIUS_FOCUS) & (summary["time_window_days"] == 60.0) & (summary["depth_strategy"] == "all") & (summary["mag_threshold"].isna())]
    rows = []
    for _, row in control.iterrows():
        ref = base[base["mainshock"] == row["mainshock"]]
        if ref.empty:
            ref = summary[summary["mainshock"] == row["mainshock"]].iloc[[0]]
        ref = ref.iloc[0]
        rows.append({
            **row.to_dict(),
            "baseline_n_total": int(ref["n_total"]),
            "baseline_pre_rate": float(ref["pre_rate"]),
            "baseline_post_rate": float(ref["post_rate"]),
            "baseline_rate_ratio": float(ref["rate_ratio"]),
            "relative_control_rate": float(row["control_rate_per_day"] / ref["pre_rate"]) if ref["pre_rate"] > 0 else np.nan,
        })
    out = pd.DataFrame(rows)
    out.to_csv(CONTROL_SUMMARY_CSV, index=False)
    return out


def save_figure_data(seq: pd.DataFrame, summary: pd.DataFrame, control: pd.DataFrame) -> None:
    for mainshock, sdf in seq.groupby("mainshock"):
        sdf.to_csv(FIG_DATA_DIR / f"{mainshock}_event_centered_subset.csv", index=False)
    summary.to_csv(FIG_DATA_DIR / "all_sequence_summary.csv", index=False)
    control.to_csv(FIG_DATA_DIR / "control_table.csv", index=False)


def main() -> None:
    clean_output_dir()
    log("[1] Loading extraction outputs and source metadata")
    seq, summary, counts, control, meta, verification, mecha, station, catalog, main = load_inputs()
    require_columns(seq, ["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "time_rel_days", "radial_distance_km", "dep", "mag"], "event_centered_sequence_table")
    require_columns(summary, ["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "n_total", "n_pre", "n_post"], "sequence_diagnostics_summary")
    require_columns(meta, ["mainshock", "matched_datetime", "matched_lat", "matched_lon", "matched_dep", "matched_mag"], "mainshock_sequence_metadata")

    seq = add_window_columns(seq)
    summary = summary.copy()
    summary["mag_threshold"] = summary["mag_threshold"].where(~pd.isna(summary["mag_threshold"]), np.nan)
    counts = counts.copy()
    control = control.copy()

    # Some source-context columns for interpretation
    mecha_summary_rows = []
    for _, mr in meta.iterrows():
        mr_seq = seq[(seq["mainshock"] == mr["mainshock"]) & (seq["radius_km"] == RADIUS_FOCUS) & (seq["time_window_days"] == TIME_FOCUS_DAYS) & (seq["depth_strategy"] == "all") & (seq["mag_threshold"].isna())]
        mecha_summary_rows.append({"mainshock": mr["mainshock"], **summarize_mecha(mr_seq, mecha, mr)})
    mecha_summary = pd.DataFrame(mecha_summary_rows)

    # Metrics table aggregated across the full parameter grid
    summary.to_csv(SUMMARY_CSV, index=False)
    control = save_control_summary(control, summary)
    mecha_summary.to_csv(MECHA_CSV, index=False)
    save_distribution_tables(summary, seq)
    rate_df = save_window_rates(seq)
    robustness = build_robustness(summary)
    robustness.to_csv(ROBUSTNESS_CSV, index=False)
    comparison = build_three_sequence_comparison(summary)
    comparison.to_csv(COMPARISON_CSV, index=False)
    save_figure_data(seq, summary, control)

    # long-format summary for key figure-ready diagnostics
    diag_rows = []
    for _, row in summary.iterrows():
        diag_rows.append({
            "mainshock": row["mainshock"],
            "radius_km": row["radius_km"],
            "time_window_days": row["time_window_days"],
            "depth_strategy": row["depth_strategy"],
            "mag_threshold": row["mag_threshold"],
            "metric": "n_total",
            "value": row["n_total"],
        })
        diag_rows.append({
            "mainshock": row["mainshock"],
            "radius_km": row["radius_km"],
            "time_window_days": row["time_window_days"],
            "depth_strategy": row["depth_strategy"],
            "mag_threshold": row["mag_threshold"],
            "metric": "rate_ratio",
            "value": row["rate_ratio"],
        })
        diag_rows.append({
            "mainshock": row["mainshock"],
            "radius_km": row["radius_km"],
            "time_window_days": row["time_window_days"],
            "depth_strategy": row["depth_strategy"],
            "mag_threshold": row["mag_threshold"],
            "metric": "post_omori_p",
            "value": row["post_omori_p"],
        })
    pd.DataFrame(diag_rows).to_csv(SUMMARY_CSV.with_name("sequence_diagnostics_long.csv"), index=False)

    # Master verification output
    verification_out = {
        "source_verification": verification,
        "n_sequence_rows": int(len(seq)),
        "n_summary_rows": int(len(summary)),
        "n_rate_bins": int(len(rate_df)),
        "n_robustness_rows": int(len(robustness)),
        "n_comparison_rows": int(len(comparison)),
        "n_mecha_summary_rows": int(len(mecha_summary)),
        "mainshock_summary": comparison.to_dict(orient="records"),
        "sequence_grid": {
            "radii_km": sorted(summary["radius_km"].dropna().unique().tolist()),
            "time_windows_days": sorted(summary["time_window_days"].dropna().unique().tolist()),
            "depth_strategies": sorted(summary["depth_strategy"].dropna().unique().tolist()),
            "mag_thresholds": sorted([float(x) for x in pd.to_numeric(summary["mag_threshold"], errors="coerce").dropna().unique().tolist()]),
        },
    }
    with open(OUTPUT_DIR / "sequence_diagnostics_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_out, f, indent=2, default=to_jsonable)

    log(f"[2] Saved summary table to {SUMMARY_CSV}")
    log(f"[2] Saved time-binned rates to {WINDOW_CSV}")
    log(f"[2] Saved distribution tables to {MAG_CSV}, {DEPTH_CSV}, {RADIAL_CSV}")
    log(f"[2] Saved robustness table to {ROBUSTNESS_CSV}")
    log(f"[2] Saved three-sequence comparison to {COMPARISON_CSV}")
    log(f"[2] Saved control summary to {CONTROL_SUMMARY_CSV}")
    log(f"[2] Saved mechanism summary to {MECHA_CSV}")
    log("[3] Sequence comparison preview:")
    preview = comparison.to_string(index=False)
    log(preview)
    log("[4] Diagnostics completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
