import json
import math
import os
import sys
import traceback
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from obspy import read as obspy_read
from scipy.signal import correlate

BASE_PATH = Path("<WAVEFORM_DATA_ROOT>")
OBSERVATIONS_CSV = BASE_PATH / "metadata" / "observations.csv"
EVENT_PAIR_CSV = BASE_PATH / "metadata" / "event_pair_common_observations.csv"
EVENTS_CSV = BASE_PATH / "metadata" / "events.csv"
STATIONS_CSV = BASE_PATH / "metadata" / "stations.csv"

SCRIPT_PATH = Path("<CASE_ROOT>/run/02_repeat_earthquake/exp_run/scripts/01_repeat_event_analysis.py")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_repeat_earthquake/exp_run/outputs/01_repeat_event_analysis")

TIME_START = pd.Timestamp("2025-11-01T00:00:00")
TIME_END = pd.Timestamp("2025-12-07T00:00:00")

REQUESTED_CORES = 64
PHASE_WINDOW = (-0.5, 5.5)
FILTER_BAND = (2.0, 15.0)
MAX_LAG_S = 1.5
MIN_COMPONENTS_USED = 8
MIN_STATIONS_USED = 3
LOOSE_CC_THRESHOLD = 0.55
STRICT_CC_THRESHOLD = 0.70
CANDIDATE_LIMIT_MODE = "all"  # "all" or "ranked_top"
MAX_CANDIDATES = 5000
RESUME_EXISTING = True

PAIR_BATCH_LOG_EVERY = 100

OBS_USECOLS = [
    "evid",
    "origin_time",
    "event_latitude",
    "event_longitude",
    "event_depth_km",
    "event_magnitude",
    "station_id",
    "station_code",
    "station_latitude",
    "station_longitude",
    "component",
    "station_component",
    "sac_file",
    "exists",
    "has_p_pick",
    "has_s_pick",
    "p_time_after_origin_s",
    "s_time_after_origin_s",
    "sampling_rate_hz",
    "npts",
    "start_time",
    "end_time",
]

PAIR_RENAME_MAP = {
    "event_i": "event_id_1",
    "event_j": "event_id_2",
    "origin_i": "origin_time_1",
    "origin_j": "origin_time_2",
    "lat_i": "latitude_1",
    "lon_i": "longitude_1",
    "dep_i_km": "depth_km_1",
    "mag_i": "magnitude_1",
    "lat_j": "latitude_2",
    "lon_j": "longitude_2",
    "dep_j_km": "depth_km_2",
    "mag_j": "magnitude_2",
    "horizontal_distance_km": "epicentral_distance_km",
    "depth_distance_km": "depth_diff_km",
    "time_separation_s": "time_diff_s",
}

WORKER_OBS_INDEX = None
WORKER_TRACE_CACHE = None
WORKER_EVENT_COMPONENTS = None


@dataclass
class TraceWindowResult:
    data: Optional[np.ndarray]
    sampling_rate_hz: Optional[float]
    failure_reason: Optional[str]


def log(msg: str) -> None:
    print(msg, flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repeat-earthquake candidate analysis.")
    parser.add_argument("--base-path", type=Path, default=BASE_PATH)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--time-start", default=str(TIME_START))
    parser.add_argument("--time-end", default=str(TIME_END))
    parser.add_argument("--requested-cores", type=int, default=REQUESTED_CORES)
    parser.add_argument("--candidate-limit-mode", choices=["all", "ranked_top"], default=CANDIDATE_LIMIT_MODE)
    parser.add_argument("--max-candidates", type=int, default=MAX_CANDIDATES)
    parser.add_argument("--resume-existing", action=argparse.BooleanOptionalAction, default=RESUME_EXISTING)
    return parser.parse_args()


def apply_runtime_args(args: argparse.Namespace) -> None:
    global BASE_PATH, OBSERVATIONS_CSV, EVENT_PAIR_CSV, EVENTS_CSV, STATIONS_CSV
    global OUTPUT_DIR, TIME_START, TIME_END, REQUESTED_CORES
    global CANDIDATE_LIMIT_MODE, MAX_CANDIDATES, RESUME_EXISTING

    BASE_PATH = args.base_path
    OBSERVATIONS_CSV = BASE_PATH / "metadata" / "observations.csv"
    EVENT_PAIR_CSV = BASE_PATH / "metadata" / "event_pair_common_observations.csv"
    EVENTS_CSV = BASE_PATH / "metadata" / "events.csv"
    STATIONS_CSV = BASE_PATH / "metadata" / "stations.csv"
    OUTPUT_DIR = args.output_dir
    TIME_START = pd.Timestamp(args.time_start)
    TIME_END = pd.Timestamp(args.time_end)
    REQUESTED_CORES = args.requested_cores
    CANDIDATE_LIMIT_MODE = args.candidate_limit_mode
    MAX_CANDIDATES = args.max_candidates
    RESUME_EXISTING = args.resume_existing


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if RESUME_EXISTING:
        return
    stale_files = [
        OUTPUT_DIR / "candidate_event_pairs.csv",
        OUTPUT_DIR / "station_component_cc.csv",
        OUTPUT_DIR / "repeat_event_pairs.csv",
        OUTPUT_DIR / "repeat_event_families.csv",
        OUTPUT_DIR / "repeat_family_members.csv",
        OUTPUT_DIR / "analysis_summary.json",
    ]
    for stale_file in stale_files:
        if stale_file.exists():
            stale_file.unlink()


def pair_key_df(df: pd.DataFrame) -> pd.Series:
    return df["event_id_1"].astype(str) + "||" + df["event_id_2"].astype(str)


def normalize_event_id_columns(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    df = df.copy()
    if columns is None:
        columns = ["event_id_1", "event_id_2"]
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df


def load_existing_results() -> Tuple[pd.DataFrame, pd.DataFrame, set[str]]:
    pair_path = OUTPUT_DIR / "repeat_event_pairs.csv"
    station_path = OUTPUT_DIR / "station_component_cc.csv"
    if not RESUME_EXISTING or not pair_path.exists() or not station_path.exists():
        return pd.DataFrame(), pd.DataFrame(), set()

    log(f"Resume enabled: loading existing results from {OUTPUT_DIR}")
    existing_pairs = pd.read_csv(pair_path)
    existing_station = pd.read_csv(station_path)
    if {"event_id_1", "event_id_2"} - set(existing_pairs.columns):
        return pd.DataFrame(), pd.DataFrame(), set()
    existing_pairs = normalize_event_id_columns(existing_pairs)
    existing_station = normalize_event_id_columns(existing_station)
    done_keys = set(pair_key_df(existing_pairs))
    log(f"Resume enabled: found {len(done_keys)} completed event pairs")
    return existing_pairs, existing_station, done_keys


def archive_existing_results_for_resume() -> Optional[Path]:
    if not RESUME_EXISTING:
        return None
    existing_files = [
        OUTPUT_DIR / "candidate_event_pairs.csv",
        OUTPUT_DIR / "station_component_cc.csv",
        OUTPUT_DIR / "repeat_event_pairs.csv",
        OUTPUT_DIR / "repeat_event_families.csv",
        OUTPUT_DIR / "repeat_family_members.csv",
        OUTPUT_DIR / "analysis_summary.json",
    ]
    if not any(path.exists() for path in existing_files):
        return None
    archive_dir = OUTPUT_DIR / "resume_archive" / datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir.mkdir(parents=True, exist_ok=True)
    for path in existing_files:
        if path.exists():
            copy2(path, archive_dir / path.name)
    return archive_dir


def parse_time_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def audit_observations(obs: pd.DataFrame, window_obs: pd.DataFrame) -> Dict[str, object]:
    exists_series = obs["exists"].fillna(False).astype(bool)
    sac_nonempty = obs["sac_file"].fillna("").astype(str).str.len() > 0
    sample_check_n = min(2000, len(window_obs))
    sample_exists_rate = None
    if sample_check_n > 0:
        sample_paths = window_obs["sac_file"].dropna().astype(str).head(sample_check_n)
        if len(sample_paths) > 0:
            sample_exists_rate = float(np.mean([Path(p).exists() for p in sample_paths]))
    audit = {
        "n_rows_all": int(len(obs)),
        "n_rows_window": int(len(window_obs)),
        "n_events_window": int(window_obs["evid"].nunique()),
        "n_stations_window": int(window_obs["station_id"].nunique()),
        "n_station_components_window": int(window_obs["station_component"].nunique()),
        "exists_true_rate_all": float(exists_series.mean()) if len(obs) else 0.0,
        "sac_file_nonempty_rate_all": float(sac_nonempty.mean()) if len(obs) else 0.0,
        "sample_sac_path_exists_rate_window": sample_exists_rate,
        "has_p_pick_rate_window": float(window_obs["has_p_pick"].fillna(False).astype(bool).mean()) if len(window_obs) else 0.0,
        "has_s_pick_rate_window": float(window_obs["has_s_pick"].fillna(False).astype(bool).mean()) if len(window_obs) else 0.0,
        "has_both_p_s_pick_rate_window": float((window_obs["has_p_pick"].fillna(False).astype(bool) & window_obs["has_s_pick"].fillna(False).astype(bool)).mean()) if len(window_obs) else 0.0,
        "has_neither_pick_rate_window": float((~window_obs["has_p_pick"].fillna(False).astype(bool) & ~window_obs["has_s_pick"].fillna(False).astype(bool)).mean()) if len(window_obs) else 0.0,
    }
    return audit


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    log(f"Loading observations: {OBSERVATIONS_CSV}")
    obs = pd.read_csv(OBSERVATIONS_CSV, usecols=OBS_USECOLS, low_memory=False)
    obs = parse_time_columns(obs, ["origin_time", "start_time", "end_time"])
    obs["evid"] = obs["evid"].astype(str)
    obs["station_component"] = obs["station_component"].astype(str)
    obs["station_id"] = obs["station_id"].astype(str)
    obs["station_code"] = obs["station_code"].astype(str)
    obs["sac_file"] = obs["sac_file"].astype(str)

    log(f"Loading event pair table: {EVENT_PAIR_CSV}")
    pair_df = pd.read_csv(EVENT_PAIR_CSV, low_memory=False)
    pair_df = pair_df.rename(columns=PAIR_RENAME_MAP)
    pair_df = parse_time_columns(pair_df, ["origin_time_1", "origin_time_2"])
    pair_df["event_id_1"] = pair_df["event_id_1"].astype(str)
    pair_df["event_id_2"] = pair_df["event_id_2"].astype(str)

    log(f"Loading events: {EVENTS_CSV}")
    events = pd.read_csv(EVENTS_CSV, low_memory=False)
    events = parse_time_columns(events, ["origin_time"])
    events["evid"] = events["evid"].astype(str)

    log(f"Loading stations: {STATIONS_CSV}")
    stations = pd.read_csv(STATIONS_CSV, low_memory=False)
    return obs, pair_df, events, stations


def prepare_window_observations(obs: pd.DataFrame) -> pd.DataFrame:
    window_obs = obs[(obs["origin_time"] >= TIME_START) & (obs["origin_time"] < TIME_END)].copy()
    window_obs = window_obs.sort_values(["evid", "station_component", "s_time_after_origin_s", "p_time_after_origin_s"])
    window_obs = window_obs.drop_duplicates(subset=["evid", "station_component"], keep="first")
    return window_obs


def filter_candidate_pairs(pair_df: pd.DataFrame, window_event_ids: set) -> Tuple[pd.DataFrame, Dict[str, int], Dict[str, object]]:
    pairs = pair_df[
        pair_df["event_id_1"].isin(window_event_ids) & pair_df["event_id_2"].isin(window_event_ids)
    ].copy()

    threshold_grid_counts = {}
    common_thresholds = [20, 40, 60]
    distance_thresholds = [3, 5, 10]
    mag_thresholds = [0.8, 1.0]
    for common_min in common_thresholds:
        for dist_max in distance_thresholds:
            for mag_max in mag_thresholds:
                mask = (
                    (pairs["common_station_components"] >= common_min)
                    & (pairs["epicentral_distance_km"] <= dist_max)
                    & (pairs["magnitude_diff"] <= mag_max)
                )
                threshold_grid_counts[f"common>={common_min}|dist<={dist_max}|mag<={mag_max}"] = int(mask.sum())

    selection_steps = []
    candidate = pairs[
        (pairs["common_station_components"] >= 40)
        & (pairs["epicentral_distance_km"] <= 5.0)
        & (pairs["magnitude_diff"] <= 0.8)
    ].copy()
    selection_steps.append({"rule": "common>=40,dist<=5,mag<=0.8", "count": int(len(candidate))})

    if len(candidate) < 50:
        candidate = pairs[
            (pairs["common_station_components"] >= 20)
            & (pairs["epicentral_distance_km"] <= 5.0)
            & (pairs["magnitude_diff"] <= 1.0)
        ].copy()
        selection_steps.append({"rule": "fallback common>=20,dist<=5,mag<=1.0", "count": int(len(candidate))})

    if CANDIDATE_LIMIT_MODE == "ranked_top" and len(candidate) > MAX_CANDIDATES:
        candidate = pairs[
            (pairs["common_station_components"] >= 60)
            & (pairs["epicentral_distance_km"] <= 5.0)
            & (pairs["magnitude_diff"] <= 0.8)
        ].copy()
        selection_steps.append({"rule": "tighten common>=60,dist<=5,mag<=0.8", "count": int(len(candidate))})

    candidate = candidate.sort_values(
        ["epicentral_distance_km", "magnitude_diff", "common_station_components", "time_diff_s"],
        ascending=[True, True, False, True],
    ).copy()
    if CANDIDATE_LIMIT_MODE == "ranked_top":
        candidate = candidate.head(MAX_CANDIDATES).copy()
    candidate["candidate_rank"] = np.arange(1, len(candidate) + 1)
    candidate["prefilter_scheme"] = selection_steps[-1]["rule"] if selection_steps else "default"

    summary = {
        "n_pairs_window": int(len(pairs)),
        "n_candidates_final": int(len(candidate)),
        "selection_steps": selection_steps,
    }
    return candidate, threshold_grid_counts, summary


def build_observation_index(window_obs: pd.DataFrame) -> Tuple[Dict[Tuple[str, str], Dict[str, object]], Dict[str, List[str]]]:
    cols = [
        "evid",
        "origin_time",
        "event_latitude",
        "event_longitude",
        "event_depth_km",
        "event_magnitude",
        "station_id",
        "station_code",
        "station_latitude",
        "station_longitude",
        "component",
        "station_component",
        "sac_file",
        "exists",
        "has_p_pick",
        "has_s_pick",
        "p_time_after_origin_s",
        "s_time_after_origin_s",
        "sampling_rate_hz",
        "npts",
        "start_time",
        "end_time",
    ]
    required_cols = set(cols)
    missing = sorted(required_cols - set(window_obs.columns))
    if missing:
        raise ValueError(f"window_obs missing required columns: {missing}")

    index = {}
    event_to_components = defaultdict(list)
    for row in window_obs[cols].itertuples(index=False):
        rec = dict(zip(cols, row))
        evid = str(rec["evid"])
        station_component = str(rec["station_component"])
        index[(evid, station_component)] = rec
        event_to_components[evid].append(station_component)
    return index, dict(event_to_components)


def init_worker(obs_index: Dict[Tuple[str, str], Dict[str, object]], event_components: Dict[str, List[str]]) -> None:
    global WORKER_OBS_INDEX, WORKER_TRACE_CACHE, WORKER_EVENT_COMPONENTS
    WORKER_OBS_INDEX = obs_index
    WORKER_EVENT_COMPONENTS = event_components
    WORKER_TRACE_CACHE = {}


def get_trace_data(sac_file: str):
    global WORKER_TRACE_CACHE
    if sac_file in WORKER_TRACE_CACHE:
        return WORKER_TRACE_CACHE[sac_file]
    st = obspy_read(sac_file)
    tr = st[0]
    tr = tr.copy()
    tr.detrend("demean")
    tr.detrend("linear")
    tr.taper(max_percentage=0.05, type="cosine")
    tr.filter("bandpass", freqmin=FILTER_BAND[0], freqmax=FILTER_BAND[1], corners=4, zerophase=True)
    WORKER_TRACE_CACHE[sac_file] = tr
    return tr


def extract_phase_window(obs_rec: Dict[str, object], phase_used: str) -> TraceWindowResult:
    try:
        sac_file = str(obs_rec["sac_file"])
        if not sac_file or not Path(sac_file).exists():
            return TraceWindowResult(None, None, "missing_sac_file")

        tr = get_trace_data(sac_file)
        origin_time = pd.Timestamp(obs_rec["origin_time"]).to_pydatetime()
        phase_key = "s_time_after_origin_s" if phase_used == "S" else "p_time_after_origin_s"
        phase_after_origin = obs_rec.get(phase_key)
        if pd.isna(phase_after_origin):
            return TraceWindowResult(None, None, f"missing_{phase_used.lower()}_pick")

        from obspy import UTCDateTime

        phase_abs = UTCDateTime(origin_time) + float(phase_after_origin)
        win_start = phase_abs + PHASE_WINDOW[0]
        win_end = phase_abs + PHASE_WINDOW[1]

        tr_start = tr.stats.starttime
        tr_end = tr.stats.endtime
        if win_start < tr_start or win_end > tr_end:
            return TraceWindowResult(None, None, "window_out_of_trace_range")

        sliced = tr.copy().slice(starttime=win_start, endtime=win_end, nearest_sample=False)
        data = np.asarray(sliced.data, dtype=np.float64)
        if data.size < 10:
            return TraceWindowResult(None, None, "too_few_samples")
        if not np.all(np.isfinite(data)):
            return TraceWindowResult(None, None, "non_finite_data")
        data = data - np.mean(data)
        std = float(np.std(data))
        if std <= 0.0:
            return TraceWindowResult(None, None, "zero_variance")
        data = data / std
        return TraceWindowResult(data, float(sliced.stats.sampling_rate), None)
    except Exception:
        return TraceWindowResult(None, None, "trace_processing_error")


def compute_cross_correlation(x: np.ndarray, y: np.ndarray, sr: float) -> Dict[str, float]:
    n = min(len(x), len(y))
    x = x[:n]
    y = y[:n]
    if n < 10:
        raise ValueError("too_short_after_trim")
    corr = correlate(x, y, mode="full", method="auto") / n
    lags = np.arange(-n + 1, n) / sr
    lag_mask = np.abs(lags) <= MAX_LAG_S
    if not np.any(lag_mask):
        raise ValueError("no_lag_samples")
    corr_m = corr[lag_mask]
    lags_m = lags[lag_mask]
    idx_signed = int(np.argmax(corr_m))
    signed_peak_cc = float(corr_m[idx_signed])
    lag_at_signed = float(lags_m[idx_signed])
    idx_abs = int(np.argmax(np.abs(corr_m)))
    abs_peak_cc = float(np.abs(corr_m[idx_abs]))
    lag_at_abs = float(lags_m[idx_abs])
    positive_mask = corr_m > 0
    if np.any(positive_mask):
        pos_corr = corr_m[positive_mask]
        pos_lags = lags_m[positive_mask]
        idx_pos = int(np.argmax(pos_corr))
        positive_peak_cc = float(pos_corr[idx_pos])
        lag_at_positive = float(pos_lags[idx_pos])
    else:
        positive_peak_cc = float("nan")
        lag_at_positive = float("nan")
    return {
        "signed_peak_cc": signed_peak_cc,
        "lag_at_signed_peak_s": lag_at_signed,
        "abs_peak_cc": abs_peak_cc,
        "lag_at_abs_peak_s": lag_at_abs,
        "positive_peak_cc": positive_peak_cc,
        "lag_at_positive_peak_s": lag_at_positive,
    }


def process_pair(row_dict: Dict[str, object]) -> Tuple[List[Dict[str, object]], Dict[str, object], Counter]:
    failure_counter = Counter()
    event_id_1 = str(row_dict["event_id_1"])
    event_id_2 = str(row_dict["event_id_2"])

    comps_1 = set(WORKER_EVENT_COMPONENTS.get(event_id_1, []))
    comps_2 = set(WORKER_EVENT_COMPONENTS.get(event_id_2, []))
    common_components = sorted(comps_1 & comps_2)

    station_rows = []
    used_positive_cc = []
    used_abs_lag = []
    used_stations = set()
    num_s = 0
    num_p = 0

    for station_component in common_components:
        rec1 = WORKER_OBS_INDEX.get((event_id_1, station_component))
        rec2 = WORKER_OBS_INDEX.get((event_id_2, station_component))
        if rec1 is None or rec2 is None:
            failure_counter["missing_common_record"] += 1
            continue

        phase_used = None
        if pd.notna(rec1.get("s_time_after_origin_s")) and pd.notna(rec2.get("s_time_after_origin_s")):
            phase_used = "S"
        elif pd.notna(rec1.get("p_time_after_origin_s")) and pd.notna(rec2.get("p_time_after_origin_s")):
            phase_used = "P"
        else:
            failure_reason = "no_common_phase_pick"
            failure_counter[failure_reason] += 1
            station_rows.append({
                "event_id_1": event_id_1,
                "event_id_2": event_id_2,
                "station_id": rec1.get("station_id"),
                "station_code": rec1.get("station_code"),
                "station_component": station_component,
                "component": rec1.get("component"),
                "phase_used": None,
                "signed_peak_cc": np.nan,
                "positive_peak_cc": np.nan,
                "abs_peak_cc": np.nan,
                "lag_s": np.nan,
                "abs_lag_s": np.nan,
                "sampling_rate_hz": np.nan,
                "window_start_rel_s": PHASE_WINDOW[0],
                "window_end_rel_s": PHASE_WINDOW[1],
                "filter_low_hz": FILTER_BAND[0],
                "filter_high_hz": FILTER_BAND[1],
                "status": "failed",
                "failure_reason": failure_reason,
                "station_latitude": rec1.get("station_latitude"),
                "station_longitude": rec1.get("station_longitude"),
            })
            continue

        tr1 = extract_phase_window(rec1, phase_used)
        tr2 = extract_phase_window(rec2, phase_used)
        if tr1.failure_reason is not None or tr2.failure_reason is not None:
            failure_reason = tr1.failure_reason or tr2.failure_reason
            failure_counter[failure_reason] += 1
            station_rows.append({
                "event_id_1": event_id_1,
                "event_id_2": event_id_2,
                "station_id": rec1.get("station_id"),
                "station_code": rec1.get("station_code"),
                "station_component": station_component,
                "component": rec1.get("component"),
                "phase_used": phase_used,
                "signed_peak_cc": np.nan,
                "positive_peak_cc": np.nan,
                "abs_peak_cc": np.nan,
                "lag_s": np.nan,
                "abs_lag_s": np.nan,
                "sampling_rate_hz": tr1.sampling_rate_hz or tr2.sampling_rate_hz,
                "window_start_rel_s": PHASE_WINDOW[0],
                "window_end_rel_s": PHASE_WINDOW[1],
                "filter_low_hz": FILTER_BAND[0],
                "filter_high_hz": FILTER_BAND[1],
                "status": "failed",
                "failure_reason": failure_reason,
                "station_latitude": rec1.get("station_latitude"),
                "station_longitude": rec1.get("station_longitude"),
            })
            continue

        try:
            sr = min(float(tr1.sampling_rate_hz), float(tr2.sampling_rate_hz))
            if abs(float(tr1.sampling_rate_hz) - float(tr2.sampling_rate_hz)) > 1e-6:
                failure_reason = "sampling_rate_mismatch"
                failure_counter[failure_reason] += 1
                station_rows.append({
                    "event_id_1": event_id_1,
                    "event_id_2": event_id_2,
                    "station_id": rec1.get("station_id"),
                    "station_code": rec1.get("station_code"),
                    "station_component": station_component,
                    "component": rec1.get("component"),
                    "phase_used": phase_used,
                    "signed_peak_cc": np.nan,
                    "positive_peak_cc": np.nan,
                    "abs_peak_cc": np.nan,
                    "lag_s": np.nan,
                    "abs_lag_s": np.nan,
                    "sampling_rate_hz": sr,
                    "window_start_rel_s": PHASE_WINDOW[0],
                    "window_end_rel_s": PHASE_WINDOW[1],
                    "filter_low_hz": FILTER_BAND[0],
                    "filter_high_hz": FILTER_BAND[1],
                    "status": "failed",
                    "failure_reason": failure_reason,
                    "station_latitude": rec1.get("station_latitude"),
                    "station_longitude": rec1.get("station_longitude"),
                })
                continue
            cc = compute_cross_correlation(tr1.data, tr2.data, sr)
            status = "used" if np.isfinite(cc["positive_peak_cc"]) else "failed"
            failure_reason = None if status == "used" else "no_positive_peak"
            if status != "used":
                failure_counter[failure_reason] += 1
            row = {
                "event_id_1": event_id_1,
                "event_id_2": event_id_2,
                "station_id": rec1.get("station_id"),
                "station_code": rec1.get("station_code"),
                "station_component": station_component,
                "component": rec1.get("component"),
                "phase_used": phase_used,
                "signed_peak_cc": cc["signed_peak_cc"],
                "positive_peak_cc": cc["positive_peak_cc"],
                "abs_peak_cc": cc["abs_peak_cc"],
                "lag_s": cc["lag_at_positive_peak_s"] if np.isfinite(cc["positive_peak_cc"]) else cc["lag_at_signed_peak_s"],
                "abs_lag_s": abs(cc["lag_at_positive_peak_s"]) if np.isfinite(cc["positive_peak_cc"]) else abs(cc["lag_at_abs_peak_s"]),
                "sampling_rate_hz": sr,
                "window_start_rel_s": PHASE_WINDOW[0],
                "window_end_rel_s": PHASE_WINDOW[1],
                "filter_low_hz": FILTER_BAND[0],
                "filter_high_hz": FILTER_BAND[1],
                "status": status,
                "failure_reason": failure_reason,
                "station_latitude": rec1.get("station_latitude"),
                "station_longitude": rec1.get("station_longitude"),
            }
            station_rows.append(row)
            if status == "used":
                used_positive_cc.append(float(cc["positive_peak_cc"]))
                used_abs_lag.append(abs(float(row["lag_s"])))
                used_stations.add(str(rec1.get("station_id")))
                if phase_used == "S":
                    num_s += 1
                else:
                    num_p += 1
        except Exception:
            failure_reason = "cross_correlation_error"
            failure_counter[failure_reason] += 1
            station_rows.append({
                "event_id_1": event_id_1,
                "event_id_2": event_id_2,
                "station_id": rec1.get("station_id"),
                "station_code": rec1.get("station_code"),
                "station_component": station_component,
                "component": rec1.get("component"),
                "phase_used": phase_used,
                "signed_peak_cc": np.nan,
                "positive_peak_cc": np.nan,
                "abs_peak_cc": np.nan,
                "lag_s": np.nan,
                "abs_lag_s": np.nan,
                "sampling_rate_hz": np.nan,
                "window_start_rel_s": PHASE_WINDOW[0],
                "window_end_rel_s": PHASE_WINDOW[1],
                "filter_low_hz": FILTER_BAND[0],
                "filter_high_hz": FILTER_BAND[1],
                "status": "failed",
                "failure_reason": failure_reason,
                "station_latitude": rec1.get("station_latitude"),
                "station_longitude": rec1.get("station_longitude"),
            })

    pair_result = dict(row_dict)
    pair_result.update(
        {
            "median_cc": float(np.median(used_positive_cc)) if used_positive_cc else np.nan,
            "mean_cc": float(np.mean(used_positive_cc)) if used_positive_cc else np.nan,
            "max_cc": float(np.max(used_positive_cc)) if used_positive_cc else np.nan,
            "median_abs_lag_s": float(np.median(used_abs_lag)) if used_abs_lag else np.nan,
            "num_components_used": int(len(used_positive_cc)),
            "num_stations_used": int(len(used_stations)),
            "num_s_components_used": int(num_s),
            "num_p_components_used": int(num_p),
            "fraction_positive_components": float(len(used_positive_cc) / len(common_components)) if common_components else 0.0,
            "pair_status": "success" if len(used_positive_cc) > 0 else "failed",
        }
    )
    return station_rows, pair_result, failure_counter


def run_parallel_cc(
    candidate_pairs: pd.DataFrame,
    obs_index: Dict[Tuple[str, str], Dict[str, object]],
    event_components: Dict[str, List[str]],
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    records = candidate_pairs.to_dict(orient="records")
    actual_cores = max(1, min(REQUESTED_CORES, os.cpu_count() or 1, len(records) if records else 1))
    log(f"Running cross-correlation for {len(records)} candidate pairs with {actual_cores} workers")

    all_station_rows = []
    all_pair_rows = []
    failure_counter = Counter()
    completed = 0

    with ProcessPoolExecutor(max_workers=actual_cores, initializer=init_worker, initargs=(obs_index, event_components)) as executor:
        futures = [executor.submit(process_pair, rec) for rec in records]
        for future in as_completed(futures):
            station_rows, pair_row, pair_failures = future.result()
            all_station_rows.extend(station_rows)
            all_pair_rows.append(pair_row)
            failure_counter.update(pair_failures)
            completed += 1
            if completed % PAIR_BATCH_LOG_EVERY == 0 or completed == len(records):
                log(f"Completed {completed}/{len(records)} pairs")

    station_df = pd.DataFrame(all_station_rows)
    pair_df = pd.DataFrame(all_pair_rows)
    runtime_summary = {
        "requested_cores": REQUESTED_CORES,
        "actual_cores": actual_cores,
        "n_candidate_pairs_submitted": int(len(records)),
        "n_pair_results": int(len(pair_df)),
        "n_station_component_results": int(len(station_df)),
        "failure_reasons": dict(failure_counter),
    }
    return station_df, pair_df, runtime_summary


def classify_pairs(pair_df: pd.DataFrame) -> pd.DataFrame:
    pair_df = pair_df.copy()
    valid_mask = (
        (pair_df["num_components_used"] >= MIN_COMPONENTS_USED)
        & (pair_df["num_stations_used"] >= MIN_STATIONS_USED)
        & pair_df["median_cc"].notna()
    )
    pair_df["meets_minimum_usage"] = valid_mask
    pair_df["repeat_candidate_level"] = np.where(
        valid_mask & (pair_df["median_cc"] >= STRICT_CC_THRESHOLD),
        "high_confidence",
        np.where(valid_mask & (pair_df["median_cc"] >= LOOSE_CC_THRESHOLD), "loose", "non_repeat"),
    )
    return pair_df


def connected_components_from_edges(edges: List[Tuple[str, str]]) -> List[List[str]]:
    adjacency = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    components = []
    seen = set()
    for node in sorted(adjacency):
        if node in seen:
            continue
        stack = [node]
        comp = []
        seen.add(node)
        while stack:
            current = stack.pop()
            comp.append(current)
            for neighbor in sorted(adjacency[current], reverse=True):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(comp))
    return components


def build_families(pair_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    pair_df = normalize_event_id_columns(pair_df)
    high = pair_df[pair_df["repeat_candidate_level"] == "high_confidence"].copy()
    edges = [(row.event_id_1, row.event_id_2) for row in high.itertuples(index=False)]
    components = connected_components_from_edges(edges)
    families = []
    members = []
    for idx, comp in enumerate(sorted(components, key=len, reverse=True), start=1):
        family_id = f"F{idx:03d}"
        sub = high[high["event_id_1"].isin(comp) & high["event_id_2"].isin(comp)].copy()
        event_rows = []
        for evid in comp:
            rows = pair_df[(pair_df["event_id_1"] == evid) | (pair_df["event_id_2"] == evid)]
            ref = None
            if len(rows):
                if evid in set(rows["event_id_1"].astype(str)):
                    ref = rows.iloc[0]
                    origin_time = ref["origin_time_1"] if str(ref["event_id_1"]) == evid else ref["origin_time_2"]
                    latitude = ref["latitude_1"] if str(ref["event_id_1"]) == evid else ref["latitude_2"]
                    longitude = ref["longitude_1"] if str(ref["event_id_1"]) == evid else ref["longitude_2"]
                    depth_km = ref["depth_km_1"] if str(ref["event_id_1"]) == evid else ref["depth_km_2"]
                    magnitude = ref["magnitude_1"] if str(ref["event_id_1"]) == evid else ref["magnitude_2"]
                else:
                    ref = rows.iloc[0]
                    origin_time = ref["origin_time_2"]
                    latitude = ref["latitude_2"]
                    longitude = ref["longitude_2"]
                    depth_km = ref["depth_km_2"]
                    magnitude = ref["magnitude_2"]
                event_rows.append((evid, origin_time, latitude, longitude, depth_km, magnitude))
        if event_rows:
            origin_times = pd.to_datetime([r[1] for r in event_rows])
            magnitudes = [float(r[5]) for r in event_rows]
            lats = [float(r[2]) for r in event_rows]
            lons = [float(r[3]) for r in event_rows]
            families.append(
                {
                    "family_id": family_id,
                    "family_size": int(len(comp)),
                    "num_edges": int(len(sub)),
                    "start_time": origin_times.min(),
                    "end_time": origin_times.max(),
                    "duration_days": float((origin_times.max() - origin_times.min()).total_seconds() / 86400.0) if len(origin_times) > 1 else 0.0,
                    "median_pair_cc": float(sub["median_cc"].median()) if len(sub) else np.nan,
                    "max_pair_cc": float(sub["median_cc"].max()) if len(sub) else np.nan,
                    "magnitude_min": float(min(magnitudes)),
                    "magnitude_max": float(max(magnitudes)),
                    "latitude_min": float(min(lats)),
                    "latitude_max": float(max(lats)),
                    "longitude_min": float(min(lons)),
                    "longitude_max": float(max(lons)),
                }
            )
            for evid, origin_time, latitude, longitude, depth_km, magnitude in event_rows:
                members.append(
                    {
                        "family_id": family_id,
                        "event_id": evid,
                        "origin_time": origin_time,
                        "latitude": latitude,
                        "longitude": longitude,
                        "depth_km": depth_km,
                        "magnitude": magnitude,
                    }
                )
    family_summary = {
        "n_high_confidence_pairs": int(len(high)),
        "n_families": int(len(families)),
        "max_family_size": int(max([f["family_size"] for f in families], default=0)),
    }
    return pd.DataFrame(families), pd.DataFrame(members), family_summary


def validate_required_columns(df: pd.DataFrame, required_columns: List[str], name: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def write_outputs(candidate_pairs: pd.DataFrame, station_df: pd.DataFrame, pair_df: pd.DataFrame, families_df: pd.DataFrame, members_df: pd.DataFrame, summary: Dict[str, object]) -> None:
    validate_required_columns(
        candidate_pairs,
        [
            "event_id_1", "event_id_2", "origin_time_1", "origin_time_2", "time_diff_s",
            "latitude_1", "longitude_1", "depth_km_1", "magnitude_1",
            "latitude_2", "longitude_2", "depth_km_2", "magnitude_2",
            "epicentral_distance_km", "depth_diff_km", "magnitude_diff",
            "common_station_components", "common_stations", "candidate_rank", "prefilter_scheme",
        ],
        "candidate_pairs",
    )
    validate_required_columns(
        station_df,
        [
            "event_id_1", "event_id_2", "station_id", "station_component", "phase_used",
            "signed_peak_cc", "positive_peak_cc", "abs_peak_cc", "lag_s", "abs_lag_s",
            "sampling_rate_hz", "status", "failure_reason",
        ],
        "station_df",
    )
    validate_required_columns(
        pair_df,
        [
            "event_id_1", "event_id_2", "median_cc", "mean_cc", "max_cc", "median_abs_lag_s",
            "num_components_used", "num_stations_used", "num_s_components_used", "num_p_components_used",
            "epicentral_distance_km", "depth_diff_km", "magnitude_diff", "common_station_components",
            "repeat_candidate_level",
        ],
        "pair_df",
    )

    candidate_pairs.to_csv(OUTPUT_DIR / "candidate_event_pairs.csv", index=False)
    station_df.to_csv(OUTPUT_DIR / "station_component_cc.csv", index=False)
    pair_df.to_csv(OUTPUT_DIR / "repeat_event_pairs.csv", index=False)
    families_df.to_csv(OUTPUT_DIR / "repeat_event_families.csv", index=False)
    members_df.to_csv(OUTPUT_DIR / "repeat_family_members.csv", index=False)
    with open(OUTPUT_DIR / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)


def main() -> None:
    apply_runtime_args(parse_args())
    ensure_output_dir()
    obs, pair_df, events_df, stations_df = load_data()

    window_obs = prepare_window_observations(obs)
    window_event_ids = set(window_obs["evid"].astype(str).unique())
    observation_audit = audit_observations(obs, window_obs)
    log(f"Window observations: {len(window_obs)} rows, {len(window_event_ids)} events")

    candidate_pairs, threshold_grid_counts, prefilter_summary = filter_candidate_pairs(pair_df, window_event_ids)
    log(f"Candidate pairs selected: {len(candidate_pairs)}")

    existing_pair_df, existing_station_df, completed_pair_keys = load_existing_results()
    candidate_pairs["pair_key"] = pair_key_df(candidate_pairs)
    pairs_to_run = candidate_pairs[~candidate_pairs["pair_key"].isin(completed_pair_keys)].drop(columns=["pair_key"]).copy()
    candidate_pairs = candidate_pairs.drop(columns=["pair_key"])
    log(f"Candidate pairs already completed: {len(candidate_pairs) - len(pairs_to_run)}")
    log(f"Candidate pairs remaining to run: {len(pairs_to_run)}")

    obs_index, event_components = build_observation_index(window_obs)
    if len(pairs_to_run):
        new_station_df, new_pair_df, runtime_summary = run_parallel_cc(pairs_to_run, obs_index, event_components)
    else:
        new_station_df = pd.DataFrame()
        new_pair_df = pd.DataFrame()
        runtime_summary = {
            "requested_cores": REQUESTED_CORES,
            "actual_cores": 0,
            "n_candidate_pairs_submitted": 0,
            "n_pair_results": 0,
            "n_station_component_results": 0,
            "failure_reasons": {},
        }

    if len(existing_pair_df) and len(new_pair_df):
        repeat_pair_df = pd.concat([existing_pair_df, new_pair_df], ignore_index=True)
    elif len(existing_pair_df):
        repeat_pair_df = existing_pair_df.copy()
    else:
        repeat_pair_df = new_pair_df.copy()

    if len(existing_station_df) and len(new_station_df):
        station_df = pd.concat([existing_station_df, new_station_df], ignore_index=True)
    elif len(existing_station_df):
        station_df = existing_station_df.copy()
    else:
        station_df = new_station_df.copy()

    if len(repeat_pair_df):
        repeat_pair_df = normalize_event_id_columns(repeat_pair_df)
        repeat_pair_df = repeat_pair_df.drop_duplicates(subset=["event_id_1", "event_id_2"], keep="last").copy()
    if len(station_df):
        station_df = normalize_event_id_columns(station_df)
        station_df = station_df.drop_duplicates(subset=["event_id_1", "event_id_2", "station_component"], keep="last").copy()

    repeat_pair_df = classify_pairs(repeat_pair_df)
    families_df, members_df, family_summary = build_families(repeat_pair_df)

    pair_stats = {
        "n_pairs_total": int(len(repeat_pair_df)),
        "n_pairs_success": int((repeat_pair_df["pair_status"] == "success").sum()) if len(repeat_pair_df) else 0,
        "n_pairs_with_minimum_usage": int(repeat_pair_df["meets_minimum_usage"].sum()) if len(repeat_pair_df) else 0,
        "n_loose_pairs": int((repeat_pair_df["repeat_candidate_level"] == "loose").sum()) if len(repeat_pair_df) else 0,
        "n_high_confidence_pairs": int((repeat_pair_df["repeat_candidate_level"] == "high_confidence").sum()) if len(repeat_pair_df) else 0,
        "median_cc_distribution": {
            "min": float(repeat_pair_df["median_cc"].min()) if len(repeat_pair_df) and repeat_pair_df["median_cc"].notna().any() else None,
            "p25": float(repeat_pair_df["median_cc"].quantile(0.25)) if len(repeat_pair_df) and repeat_pair_df["median_cc"].notna().any() else None,
            "median": float(repeat_pair_df["median_cc"].median()) if len(repeat_pair_df) and repeat_pair_df["median_cc"].notna().any() else None,
            "p75": float(repeat_pair_df["median_cc"].quantile(0.75)) if len(repeat_pair_df) and repeat_pair_df["median_cc"].notna().any() else None,
            "max": float(repeat_pair_df["median_cc"].max()) if len(repeat_pair_df) and repeat_pair_df["median_cc"].notna().any() else None,
        },
    }

    station_stats = {
        "n_station_component_rows": int(len(station_df)),
        "n_used": int((station_df["status"] == "used").sum()) if len(station_df) else 0,
        "n_failed": int((station_df["status"] == "failed").sum()) if len(station_df) else 0,
        "phase_counts_used": station_df.loc[station_df["status"] == "used", "phase_used"].value_counts(dropna=False).to_dict() if len(station_df) else {},
        "top_failure_reasons": station_df.loc[station_df["status"] == "failed", "failure_reason"].value_counts().head(20).to_dict() if len(station_df) else {},
    }

    summary = {
        "base_path": str(BASE_PATH),
        "time_window": {"start": str(TIME_START), "end": str(TIME_END)},
        "parameters": {
            "phase_priority": ["S", "P"],
            "phase_window_s": list(PHASE_WINDOW),
            "filter_band_hz": list(FILTER_BAND),
            "max_lag_s": MAX_LAG_S,
            "requested_cores": REQUESTED_CORES,
            "minimum_components_used": MIN_COMPONENTS_USED,
            "minimum_stations_used": MIN_STATIONS_USED,
            "loose_cc_threshold": LOOSE_CC_THRESHOLD,
            "strict_cc_threshold": STRICT_CC_THRESHOLD,
            "candidate_limit_mode": CANDIDATE_LIMIT_MODE,
            "max_candidates": MAX_CANDIDATES,
            "resume_existing": RESUME_EXISTING,
        },
        "data_audit": observation_audit,
        "prefilter": {
            **prefilter_summary,
            "threshold_grid_counts": threshold_grid_counts,
        },
        "runtime": runtime_summary,
        "resume": {
            "enabled": RESUME_EXISTING,
            "completed_pairs_loaded": int(len(completed_pair_keys)),
            "candidate_pairs_total": int(len(candidate_pairs)),
            "candidate_pairs_skipped": int(len(candidate_pairs) - len(pairs_to_run)),
            "candidate_pairs_submitted_this_run": int(len(pairs_to_run)),
            "existing_station_component_rows_loaded": int(len(existing_station_df)),
        },
        "pair_results": pair_stats,
        "station_component_results": station_stats,
        "families": family_summary,
        "output_files": {
            "candidate_event_pairs.csv": str(OUTPUT_DIR / "candidate_event_pairs.csv"),
            "station_component_cc.csv": str(OUTPUT_DIR / "station_component_cc.csv"),
            "repeat_event_pairs.csv": str(OUTPUT_DIR / "repeat_event_pairs.csv"),
            "repeat_event_families.csv": str(OUTPUT_DIR / "repeat_event_families.csv"),
            "repeat_family_members.csv": str(OUTPUT_DIR / "repeat_family_members.csv"),
            "analysis_summary.json": str(OUTPUT_DIR / "analysis_summary.json"),
        },
        "notes": [
            "Baseline uses exact station_component matching with S-priority then P fallback.",
            "Depth difference is recorded but not used as a hard prefilter threshold.",
            "Event pair screening uses the precomputed common-observation table; resume mode skips event pairs already present in repeat_event_pairs.csv.",
        ],
    }

    archive_dir = archive_existing_results_for_resume()
    if archive_dir is not None:
        summary["resume"]["archive_before_overwrite"] = str(archive_dir)

    write_outputs(candidate_pairs, station_df, repeat_pair_df, families_df, members_df, summary)
    log("Analysis outputs written successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
