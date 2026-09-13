from __future__ import annotations

import json
import shutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction")

CATALOG_PATH = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MAIN_PATH = BASE_DIR / "catalog/main_earthquake.csv"
MECHA_PATH = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_PATH = BASE_DIR / "stations/station.sta"
MATCH_PATH = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch/matched_mainshocks.csv")

RADII_KM = [30, 44, 50, 80, 100]
TIME_WINDOWS_DAYS = [7, 30, 60, 90]
DEPTH_STRATEGIES = ["all", "mainshock_window", "stratified"]
MAG_THRESHOLDS = [None, 1.2, 1.5, 2.0, 2.5]
MOVING_WINDOW_DAYS = 7.0
OMORI_MIN_POST_EVENTS = 12
OMORI_MIN_SPAN_DAYS = 14.0
OMORI_BINS = 24
OUTPUT_STALE_PATTERNS = ["*.csv", "*.json", "*.txt"]


@dataclass
class SequenceResult:
    mainshock: str
    radius_km: float
    time_window_days: float
    depth_strategy: str
    mag_threshold: Optional[float]
    n_total: int
    n_pre: int
    n_post: int
    duration_pre_days: float
    duration_post_days: float
    pre_rate: float
    post_rate: float
    rate_ratio: float
    moving_rate_max: float
    moving_rate_median: float
    post_omori_c: float
    post_omori_k: float
    post_omori_p: float
    post_omori_r2: float
    post_omori_fit_ok: bool
    radial_q25_km: float
    radial_q50_km: float
    radial_q75_km: float
    depth_q25_km: float
    depth_q50_km: float
    depth_q75_km: float
    mag_q25: float
    mag_q50: float
    mag_q75: float
    mecha_events: int
    mecha_available: bool


def log(msg: str) -> None:
    print(msg, flush=True)


def to_jsonable(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.ndarray,)):
        return value.tolist()
    return value


def clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    for pattern in OUTPUT_STALE_PATTERNS:
        for p in OUTPUT_DIR.glob(pattern):
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


def load_inputs() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cat = pd.read_csv(CATALOG_PATH)
    main = pd.read_csv(MAIN_PATH)
    mecha = pd.read_csv(MECHA_PATH)
    sta = pd.read_csv(STATION_PATH)
    match = pd.read_csv(MATCH_PATH)
    cat["datetime"] = parse_time(cat["datetime"])
    main["datetime"] = parse_time(main["datetime"])
    mecha["origin_time"] = parse_time(mecha["origin_time"])
    for col in ["matched_datetime", "ref_datetime"]:
        if col in match.columns:
            match[col] = parse_time(match[col])
    return cat, main, mecha, sta, match


def verify_required_fields(cat: pd.DataFrame, main: pd.DataFrame, mecha: pd.DataFrame, sta: pd.DataFrame, match: pd.DataFrame) -> Dict[str, object]:
    def present(df, cols):
        return [c for c in cols if c not in df.columns]

    return {
        "catalog": {"required": ["datetime", "lat", "lon", "dep", "mag"], "missing": present(cat, ["datetime", "lat", "lon", "dep", "mag"])},
        "main_earthquake": {"required": ["index", "datetime", "lat", "lon", "dep", "mag"], "missing": present(main, ["index", "datetime", "lat", "lon", "dep", "mag"])},
        "mechanism": {"required": ["origin_time", "lat_deg", "lon_deg", "depth_km"], "missing": present(mecha, ["origin_time", "lat_deg", "lon_deg", "depth_km"])},
        "stations": {"required": ["latitude", "longitude"], "missing": present(sta, ["latitude", "longitude"])},
        "matched_mainshocks": {"required": ["label", "matched_datetime", "matched_lat", "matched_lon", "matched_dep", "matched_mag"], "missing": present(match, ["label", "matched_datetime", "matched_lat", "matched_lon", "matched_dep", "matched_mag"])},
    }


def add_seq_coords(df: pd.DataFrame, mainshock_row: pd.Series) -> pd.DataFrame:
    out = df.copy()
    out["time_rel_days"] = (out["datetime"] - mainshock_row["matched_datetime"]).dt.total_seconds() / 86400.0
    out["time_rel_sec"] = (out["datetime"] - mainshock_row["matched_datetime"]).dt.total_seconds()
    out["radial_distance_km"] = haversine_km(mainshock_row["matched_lat"], mainshock_row["matched_lon"], out["lat"].to_numpy(), out["lon"].to_numpy())
    out["depth_rel_km"] = out["dep"] - float(mainshock_row["matched_dep"])
    out["abs_depth_rel_km"] = out["depth_rel_km"].abs()
    out["is_post"] = out["time_rel_days"] > 0
    out["is_pre"] = out["time_rel_days"] < 0
    return out


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


def omori_fit(post_df: pd.DataFrame) -> Tuple[bool, float, float, float, float]:
    if len(post_df) < OMORI_MIN_POST_EVENTS:
        return False, np.nan, np.nan, np.nan, np.nan
    t = post_df["time_rel_days"].to_numpy()
    t = t[t > 0]
    if len(t) < OMORI_MIN_POST_EVENTS:
        return False, np.nan, np.nan, np.nan, np.nan
    span = t.max() - t.min()
    if span < OMORI_MIN_SPAN_DAYS:
        return False, np.nan, np.nan, np.nan, np.nan
    bins = np.logspace(np.log10(max(0.02, t.min())), np.log10(t.max() + 1e-6), OMORI_BINS)
    counts, edges = np.histogram(t, bins=bins)
    mids = np.sqrt(edges[:-1] * edges[1:])
    valid = counts > 0
    if valid.sum() < 4:
        return False, np.nan, np.nan, np.nan, np.nan
    x = np.log10(mids[valid])
    y = np.log10(counts[valid] / np.diff(edges)[valid])
    A = np.vstack([np.ones_like(x), -np.log10(mids[valid] + 1e-9)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    intercept, p = coef
    yhat = A @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    k = float(10 ** intercept)
    c = 0.01
    return True, c, k, float(p), float(r2)


def summarize_mecha_overlap(seq: pd.DataFrame, mecha: pd.DataFrame, mainshock_row: pd.Series) -> Tuple[int, bool]:
    if seq.empty or mecha.empty:
        return 0, False
    dts = (mecha["origin_time"] - mainshock_row["matched_datetime"]).dt.total_seconds().abs()
    dist = haversine_km(mainshock_row["matched_lat"], mainshock_row["matched_lon"], mecha["lat_deg"].to_numpy(), mecha["lon_deg"].to_numpy())
    mask = (dts <= 90 * 86400) & (dist <= 100)
    return int(mask.sum()), bool(mask.any())


def build_one_sequence(cat: pd.DataFrame, mecha: pd.DataFrame, mainshock_row: pd.Series, radius: float, tdays: float, depth_strategy: str, mag_thr: Optional[float]) -> Tuple[pd.DataFrame, SequenceResult]:
    seq = add_seq_coords(cat, mainshock_row)
    seq = seq[(seq["radial_distance_km"] <= radius) & (seq["time_rel_days"].abs() <= tdays)]
    seq = seq[depth_mask(seq, mainshock_row, depth_strategy)]
    if mag_thr is not None:
        seq = seq[seq["mag"] >= mag_thr]
    seq = seq.sort_values("datetime").reset_index(drop=True)
    pre = seq[seq["time_rel_days"] < 0]
    post = seq[seq["time_rel_days"] > 0]
    duration_pre = float(tdays)
    duration_post = float(tdays)
    pre_rate = float(len(pre) / duration_pre) if duration_pre > 0 else np.nan
    post_rate = float(len(post) / duration_post) if duration_post > 0 else np.nan
    rate_ratio = float(post_rate / pre_rate) if pre_rate and pre_rate > 0 else np.inf if post_rate > 0 else np.nan
    moving_window = max(1.0, MOVING_WINDOW_DAYS)
    moving_rates = []
    for center in np.arange(-tdays + moving_window / 2.0, tdays - moving_window / 2.0 + 1e-9, moving_window / 2.0):
        lo = center - moving_window / 2.0
        hi = center + moving_window / 2.0
        moving_rates.append(((seq["time_rel_days"] >= lo) & (seq["time_rel_days"] < hi)).sum() / moving_window)
    moving_rate_max = float(np.max(moving_rates)) if moving_rates else np.nan
    moving_rate_median = float(np.median(moving_rates)) if moving_rates else np.nan
    fit_ok, c, k, p, r2 = omori_fit(post)
    mecha_n, mecha_available = summarize_mecha_overlap(seq, mecha, mainshock_row)
    if len(seq):
        radial_q25, radial_q50, radial_q75 = np.nanpercentile(seq["radial_distance_km"], [25, 50, 75])
        depth_q25, depth_q50, depth_q75 = np.nanpercentile(seq["dep"], [25, 50, 75])
        mag_q25, mag_q50, mag_q75 = np.nanpercentile(seq["mag"], [25, 50, 75])
    else:
        radial_q25 = radial_q50 = radial_q75 = np.nan
        depth_q25 = depth_q50 = depth_q75 = np.nan
        mag_q25 = mag_q50 = mag_q75 = np.nan
    result = SequenceResult(
        mainshock=str(mainshock_row["label"]),
        radius_km=float(radius),
        time_window_days=float(tdays),
        depth_strategy=depth_strategy,
        mag_threshold=mag_thr if mag_thr is not None else np.nan,
        n_total=int(len(seq)),
        n_pre=int(len(pre)),
        n_post=int(len(post)),
        duration_pre_days=duration_pre,
        duration_post_days=duration_post,
        pre_rate=pre_rate,
        post_rate=post_rate,
        rate_ratio=rate_ratio,
        moving_rate_max=moving_rate_max,
        moving_rate_median=moving_rate_median,
        post_omori_c=c,
        post_omori_k=k,
        post_omori_p=p,
        post_omori_r2=r2,
        post_omori_fit_ok=fit_ok,
        radial_q25_km=float(radial_q25),
        radial_q50_km=float(radial_q50),
        radial_q75_km=float(radial_q75),
        depth_q25_km=float(depth_q25),
        depth_q50_km=float(depth_q50),
        depth_q75_km=float(depth_q75),
        mag_q25=float(mag_q25),
        mag_q50=float(mag_q50),
        mag_q75=float(mag_q75),
        mecha_events=mecha_n,
        mecha_available=mecha_available,
    )
    seq = seq.assign(mainshock=str(mainshock_row["label"]), radius_km=float(radius), time_window_days=float(tdays), depth_strategy=depth_strategy, mag_threshold=mag_thr)
    return seq, result


def main() -> None:
    clean_output_dir()
    log("[1] Reading catalog, mainshock match table, mechanism table, and station table")
    cat, main, mecha, sta, match = load_inputs()
    verification = verify_required_fields(cat, main, mecha, sta, match)

    if "matched_datetime" not in match.columns or match["matched_datetime"].isna().any():
        raise RuntimeError("Matched mainshock table is missing valid matched_datetime values; run task 01 first.")

    seq_tables = []
    summary_rows = []
    count_rows = []
    control_rows = []
    mainshock_seq_meta = []

    for _, mr in match.iterrows():
        label = str(mr["label"])
        log(f"[2] Building sequences for {label}")
        base_seq = add_seq_coords(cat, mr)
        base_seq = base_seq.sort_values("datetime").reset_index(drop=True)
        mainshock_seq_meta.append({
            "mainshock": label,
            "matched_index": int(mr["matched_index"]),
            "matched_datetime": mr["matched_datetime"],
            "matched_lat": float(mr["matched_lat"]),
            "matched_lon": float(mr["matched_lon"]),
            "matched_dep": float(mr["matched_dep"]),
            "matched_mag": float(mr["matched_mag"]),
            "n_catalog_events_total": int(len(base_seq)),
        })
        for radius in RADII_KM:
            for tdays in TIME_WINDOWS_DAYS:
                for depth_strategy in DEPTH_STRATEGIES:
                    for mag_thr in MAG_THRESHOLDS:
                        seq, res = build_one_sequence(cat, mecha, mr, radius, tdays, depth_strategy, mag_thr)
                        seq_tables.append(seq)
                        summary_rows.append(res.__dict__)
                        count_rows.append({
                            "mainshock": label,
                            "radius_km": radius,
                            "time_window_days": tdays,
                            "depth_strategy": depth_strategy,
                            "mag_threshold": np.nan if mag_thr is None else mag_thr,
                            "n_events": int(len(seq)),
                            "n_pre": int((seq["time_rel_days"] < 0).sum()),
                            "n_post": int((seq["time_rel_days"] > 0).sum()),
                            "has_post_omori_fit": bool(res.post_omori_fit_ok),
                        })
        # simple control: background window away from the mainshock, matching the same radius and duration
        shifted = add_seq_coords(cat, mr)
        control_lo = -240.0
        control_hi = -180.0
        control = shifted[(shifted["radial_distance_km"] <= 50) & (shifted["time_rel_days"] >= control_lo) & (shifted["time_rel_days"] < control_hi)]
        control_rows.append({"mainshock": label, "control_window_days": 60, "control_time_lo_days": control_lo, "control_time_hi_days": control_hi, "control_radius_km": 50, "control_n_events": int(len(control)), "control_rate_per_day": float(len(control) / 60.0)})

    seq_df = pd.concat(seq_tables, ignore_index=True) if seq_tables else pd.DataFrame()
    summary_df = pd.DataFrame(summary_rows)
    count_df = pd.DataFrame(count_rows)
    control_df = pd.DataFrame(control_rows)
    mainshock_meta_df = pd.DataFrame(mainshock_seq_meta)

    required_downstream = ["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "time_rel_days", "radial_distance_km", "depth_rel_km"]
    missing = [c for c in required_downstream if c not in seq_df.columns]
    if missing:
        raise RuntimeError(f"Sequence table missing required downstream columns: {missing}")

    seq_path = OUTPUT_DIR / "event_centered_sequence_table.csv"
    summary_path = OUTPUT_DIR / "sequence_diagnostics_summary.csv"
    counts_path = OUTPUT_DIR / "sequence_extraction_counts.csv"
    control_path = OUTPUT_DIR / "sequence_control_comparison.csv"
    meta_path = OUTPUT_DIR / "mainshock_sequence_metadata.csv"
    verification_path = OUTPUT_DIR / "sequence_extraction_verification.json"

    seq_df.to_csv(seq_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    count_df.to_csv(counts_path, index=False)
    control_df.to_csv(control_path, index=False)
    mainshock_meta_df.to_csv(meta_path, index=False)
    with open(verification_path, "w", encoding="utf-8") as f:
        json.dump({
            "inputs": verification,
            "n_mainshocks": int(len(match)),
            "n_sequences": int(len(seq_df)),
            "n_sequence_rows": int(len(summary_df)),
            "count_grid_size": int(len(count_df)),
            "control_rows": int(len(control_df)),
            "mainshocks": [to_jsonable(v) for v in mainshock_seq_meta],
            "parameter_grid": {
                "radii_km": RADII_KM,
                "time_windows_days": TIME_WINDOWS_DAYS,
                "depth_strategies": DEPTH_STRATEGIES,
                "mag_thresholds": MAG_THRESHOLDS,
                "moving_window_days": MOVING_WINDOW_DAYS,
            },
        }, f, indent=2, default=str)

    log(f"[3] Saved sequence table to {seq_path}")
    log(f"[3] Saved summary table to {summary_path}")
    log(f"[3] Saved count matrix to {counts_path}")
    log(f"[3] Saved control comparison to {control_path}")
    log(f"[3] Saved mainshock metadata to {meta_path}")
    log("[4] Sequence summary preview:")
    preview_cols = ["mainshock", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "n_total", "n_pre", "n_post", "rate_ratio", "post_omori_fit_ok", "post_omori_r2"]
    log(summary_df[preview_cols].head(15).to_string(index=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
