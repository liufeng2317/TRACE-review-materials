import importlib.util
import json
import math
import os
import sys
import traceback
from collections import defaultdict

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from obspy import UTCDateTime, read
from pyproj import Proj


SCRIPT_PATH = Path(__file__).resolve()
OUTPUT_DIR = Path(
    "<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude"
)
PICKS_DIR = Path(
    "<CASE_ROOT>/catalog_construction/01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking"
)
STATION_FILE = Path(
    "<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta"
)
WA_BASE_DIR = Path(
    "<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/magnitude_wood_anderson"
)
START_DATE = UTCDateTime("2019-07-04T00:00:00Z")
END_DATE = UTCDateTime("2019-07-26T00:00:00Z")
PROCESS_DAY_KEYS = [
    f"201907{day:02d}" for day in range(4, 26)
]
MAX_CORES = 64
NCPU = min(MAX_CORES, os.cpu_count() or 1)

VELOCITY_DEPTHS_KM = [0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
VP_KMPS = [4.96, 5.14, 5.45, 6.07, 6.12, 6.24, 7.12]
VS_KMPS = [v / 1.73 for v in VP_KMPS]
DEPTH_RANGE_KM = [0.0, 30.0]

DBSCAN_EPS_KM = 15.0
DBSCAN_MIN_SAMPLES = 3
DBSCAN_MIN_CLUSTER_SIZE = 3
DBSCAN_MAX_TIME_SPACE_RATIO = 5.0
OVERSAMPLE_FACTOR = 5
MAG_WINDOW_PRE_S = 0.5
MAG_WINDOW_POST_S = 3.0
MAG_WINDOW_PRE_P = 0.2
MAG_WINDOW_POST_P = 1.0
MIN_STATIONS_FOR_MAG = 1



def log(message: str) -> None:
    print(message, flush=True)


def ensure_clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for pattern in [
        "catalog_*.dat",
        "phase_*.dat",
        "*.png",
        "*.csv",
        "*.json",
    ]:
        for path in OUTPUT_DIR.glob(pattern):
            if path.is_file() or path.is_symlink():
                path.unlink()
            else:
                raise IsADirectoryError(f"Unexpected directory inside output dir: {path}")



def import_gamma_association():
    gamma_spec = importlib.util.find_spec("gamma")
    if gamma_spec is not None:
        from gamma.utils import association  # type: ignore
        return association, "gamma"
    gamma_upper_spec = importlib.util.find_spec("GaMMA")
    if gamma_upper_spec is not None:
        from GaMMA.gamma.utils import association  # type: ignore
        return association, "GaMMA.gamma"
    raise ModuleNotFoundError(
        "Could not import GaMMA association function from 'gamma.utils' or 'GaMMA.gamma.utils'."
    )



def utc_to_str(value) -> str:
    if value is None:
        return "-1"
    if isinstance(value, str):
        if value == "-1":
            return value
        return str(UTCDateTime(value))
    if isinstance(value, UTCDateTime):
        return str(value)
    if pd.isna(value):
        return "-1"
    return str(UTCDateTime(pd.Timestamp(value).to_pydatetime()))



def parse_station_metadata() -> tuple[pd.DataFrame, Proj, dict]:
    log(f"[station] reading {STATION_FILE}")
    rows = []
    with open(STATION_FILE, "r", encoding="utf-8") as fobj:
        for line_no, line in enumerate(fobj, start=1):
            text = line.strip()
            if not text:
                continue
            parts = [item.strip() for item in text.split(",")]
            if len(parts) < 4:
                raise ValueError(f"Station line {line_no} has fewer than 4 columns: {text}")
            station_id, lat, lon, elev = parts[:4]
            rows.append(
                {
                    "id": station_id,
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "elevation_m": float(elev),
                }
            )
    stations = pd.DataFrame(rows).drop_duplicates(subset=["id"]).sort_values("id").reset_index(drop=True)
    if stations.empty:
        raise ValueError("No stations parsed from station.sta")
    required_station_cols = ["id", "latitude", "longitude", "elevation_m"]
    missing_station_cols = [col for col in required_station_cols if col not in stations.columns]
    if missing_station_cols:
        raise ValueError(f"Station table missing required columns: {missing_station_cols}")

    lon0 = float(stations["longitude"].median())
    lat0 = float(stations["latitude"].median())
    proj = Proj(f"+proj=aeqd +lon_0={lon0} +lat_0={lat0} +units=km +datum=WGS84")
    xy = stations.apply(lambda r: pd.Series(proj(r["longitude"], r["latitude"])), axis=1)
    xy.columns = ["x(km)", "y(km)"]
    stations = pd.concat([stations, xy], axis=1)
    stations["z(km)"] = -stations["elevation_m"] / 1000.0
    region = {
        "lon_min": float(stations["longitude"].min()),
        "lon_max": float(stations["longitude"].max()),
        "lat_min": float(stations["latitude"].min()),
        "lat_max": float(stations["latitude"].max()),
        "x_min": float(stations["x(km)"].min()),
        "x_max": float(stations["x(km)"].max()),
        "y_min": float(stations["y(km)"].min()),
        "y_max": float(stations["y(km)"].max()),
        "z_min": DEPTH_RANGE_KM[0],
        "z_max": DEPTH_RANGE_KM[1],
        "proj_lon0": lon0,
        "proj_lat0": lat0,
    }
    stations.to_csv(OUTPUT_DIR / "stations_projected.csv", index=False)
    with open(OUTPUT_DIR / "region_summary.json", "w", encoding="utf-8") as fobj:
        json.dump(region, fobj, indent=2)
    log(f"[station] parsed {len(stations)} stations")
    return stations, proj, region


def build_gamma_config(region: dict) -> dict:
    config = {
        "dims": ["x(km)", "y(km)", "z(km)"],
        "use_dbscan": True,
        "use_amplitude": True,
        "oversample_factor": OVERSAMPLE_FACTOR,
        "method": "BGMM",
        "ncpu": NCPU,
        "dbscan_eps": DBSCAN_EPS_KM,
        "dbscan_min_samples": DBSCAN_MIN_SAMPLES,
        "dbscan_min_cluster_size": DBSCAN_MIN_CLUSTER_SIZE,
        "dbscan_max_time_space_ratio": DBSCAN_MAX_TIME_SPACE_RATIO,
        "min_picks_per_eq": 5,
        "min_p_picks_per_eq": 0,
        "min_s_picks_per_eq": 0,
        "max_sigma11": 3.0,
        "max_sigma22": 1.0,
        "max_sigma12": 1.0,
        "vel": {"p": VP_KMPS[0], "s": VS_KMPS[0]},
        "x(km)": [region["x_min"], region["x_max"]],
        "y(km)": [region["y_min"], region["y_max"]],
        "z(km)": DEPTH_RANGE_KM,
        "bfgs_bounds": (
            (region["x_min"] - 1.0, region["x_max"] + 1.0),
            (region["y_min"] - 1.0, region["y_max"] + 1.0),
            (DEPTH_RANGE_KM[0], DEPTH_RANGE_KM[1] + 1.0),
            (None, None),
        ),
        "eikonal": {
            "vel": {"z": VELOCITY_DEPTHS_KM, "p": VP_KMPS, "s": VS_KMPS},
            "h": 1.0,
            "xlim": [region["x_min"], region["x_max"]],
            "ylim": [region["y_min"], region["y_max"]],
            "zlim": DEPTH_RANGE_KM,
        },
    }
    return config


def load_daily_picks(day_key: str, station_ids: set[str]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    pick_file = PICKS_DIR / f"picks_{day_key}.csv"
    if not pick_file.exists():
        raise FileNotFoundError(f"Missing pick file: {pick_file}")
    log(f"[pick:{day_key}] reading {pick_file}")
    picks = pd.read_csv(pick_file)
    required = ["station_id", "phase_time", "phase_score", "phase_amplitude", "phase_type"]
    missing = [col for col in required if col not in picks.columns]
    if missing:
        raise ValueError(f"Pick file {pick_file} missing columns: {missing}")
    picks = picks[required].copy()
    picks = picks[picks["phase_type"].isin(["P", "S"])].copy()
    picks["station_id"] = picks["station_id"].astype(str)
    picks = picks[picks["station_id"].isin(station_ids)].copy()
    picks["timestamp"] = pd.to_datetime(picks["phase_time"], utc=True)
    picks["prob"] = picks["phase_score"].astype(float)
    picks["amp"] = picks["phase_amplitude"].astype(float)
    picks["type"] = picks["phase_type"].astype(str)
    picks = picks.reset_index(drop=True)
    picks["pick_index"] = np.arange(len(picks), dtype=int)
    picks["id"] = picks["station_id"]

    gamma_picks = picks[["id", "timestamp", "prob", "amp", "type"]].copy()
    gamma_picks.index = picks["pick_index"].values
    qc = {
        "day": day_key,
        "total_picks": int(len(picks)),
        "p_picks": int((picks["type"] == "P").sum()),
        "s_picks": int((picks["type"] == "S").sum()),
        "stations": int(picks["station_id"].nunique()),
        "missing_amp_count": int((picks["amp"] == -1).sum()),
    }
    return picks, gamma_picks, qc


def run_gamma_for_day(day_key: str, master_picks: pd.DataFrame, gamma_picks: pd.DataFrame, stations: pd.DataFrame, proj: Proj, config: dict, association_func):
    required_pick_cols = ["pick_index", "station_id", "timestamp", "prob", "amp", "type"]
    missing_pick_cols = [col for col in required_pick_cols if col not in master_picks.columns]
    if missing_pick_cols:
        raise ValueError(f"Master pick table missing required columns for {day_key}: {missing_pick_cols}")
    required_gamma_cols = ["id", "timestamp", "prob", "amp", "type"]
    missing_gamma_cols = [col for col in required_gamma_cols if col not in gamma_picks.columns]
    if missing_gamma_cols:
        raise ValueError(f"GaMMA pick table missing required columns for {day_key}: {missing_gamma_cols}")
    required_station_cols = ["id", "longitude", "latitude", "elevation_m", "x(km)", "y(km)", "z(km)"]
    missing_station_cols = [col for col in required_station_cols if col not in stations.columns]
    if missing_station_cols:
        raise ValueError(f"Station table missing required GaMMA columns: {missing_station_cols}")
    log(f"[gamma:{day_key}] starting association with {len(gamma_picks)} picks using {NCPU} cores")
    events, assignments = association_func(gamma_picks, stations.copy(), config, 0, config["method"])
    if events is None or len(events) == 0:

        log(f"[gamma:{day_key}] no events returned")
        events_df = pd.DataFrame(columns=["event_index", "time", "magnitude", "x(km)", "y(km)", "z(km)"])
        assignments_df = pd.DataFrame(columns=["pick_index", "event_index", "gamma_score"])
    else:
        events_df = pd.DataFrame(events)
        assignments_df = pd.DataFrame(assignments, columns=["pick_index", "event_index", "gamma_score"])
        lonlat = events_df.apply(lambda r: pd.Series(proj(r["x(km)"], r["y(km)"], inverse=True)), axis=1)
        lonlat.columns = ["longitude", "latitude"]
        events_df = pd.concat([events_df, lonlat], axis=1)
        events_df["depth_km"] = events_df["z(km)"].astype(float).clip(lower=DEPTH_RANGE_KM[0], upper=DEPTH_RANGE_KM[1])
        events_df["z(km)"] = events_df["depth_km"]
        events_df["origin_time"] = events_df["time"].apply(lambda x: str(UTCDateTime(pd.Timestamp(x).to_pydatetime())))
        if "magnitude" not in events_df.columns:
            events_df["magnitude"] = np.nan

    joined = master_picks.copy()
    if len(assignments_df) > 0:
        joined = joined.merge(assignments_df, on="pick_index", how="left")
    else:
        joined["event_index"] = np.nan
        joined["gamma_score"] = np.nan
    joined["event_index"] = joined["event_index"].fillna(-1).astype(int)
    joined["gamma_score"] = joined["gamma_score"].fillna(-1.0)
    log(f"[gamma:{day_key}] finished with {len(events_df)} events and {(joined['event_index']!=-1).sum()} assigned picks")
    return events_df, assignments_df, joined


def choose_best_pick(group: pd.DataFrame, phase_type: str):
    subset = group[group["type"] == phase_type].copy()
    if subset.empty:
        return None
    subset = subset.sort_values(["prob", "timestamp"], ascending=[False, True])
    return subset.iloc[0]


def pair_event_phases(events_df: pd.DataFrame, assigned_picks: pd.DataFrame) -> pd.DataFrame:
    records = []
    if events_df.empty:
        return pd.DataFrame(records)
    event_lookup = events_df.set_index("event_index").to_dict(orient="index")
    assigned = assigned_picks[assigned_picks["event_index"] != -1].copy()
    for (event_index, station_id), group in assigned.groupby(["event_index", "station_id"]):
        event = event_lookup.get(event_index)
        if event is None:
            continue
        best_p = choose_best_pick(group, "P")
        best_s = choose_best_pick(group, "S")
        p_time = utc_to_str(best_p["timestamp"]) if best_p is not None else "-1"
        s_time = utc_to_str(best_s["timestamp"]) if best_s is not None else "-1"
        p_amp = float(best_p["amp"]) if best_p is not None else np.nan
        s_amp = float(best_s["amp"]) if best_s is not None else np.nan
        if best_p is None and best_s is None:
            phase_amp = -1.0
        elif not np.isnan(s_amp):
            phase_amp = float(s_amp)
        elif not np.isnan(p_amp):
            phase_amp = float(p_amp)
        else:
            phase_amp = -1.0
        records.append(
            {
                "event_index": int(event_index),
                "station_id": station_id,
                "p_pick_time": p_time,
                "s_pick_time": s_time,
                "phase_amplitude": phase_amp,
                "origin_time": event["origin_time"],
                "event_latitude": float(event["latitude"]),
                "event_longitude": float(event["longitude"]),
                "event_depth_km": float(event["depth_km"]),
                "event_magnitude": float(event.get("magnitude", np.nan)) if not pd.isna(event.get("magnitude", np.nan)) else np.nan,
            }
        )
    paired = pd.DataFrame(records).sort_values(["event_index", "station_id"]).reset_index(drop=True) if records else pd.DataFrame(records)
    return paired



def haversine_km(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    return 6371.0 * 2.0 * math.asin(math.sqrt(a))


def estimate_local_magnitude(amplitude_mm: float, hypocentral_distance_km: float) -> float:
    amplitude_mm = max(amplitude_mm, 1e-6)
    hypocentral_distance_km = max(hypocentral_distance_km, 1.0)
    return float(math.log10(amplitude_mm) + 1.11 * math.log10(hypocentral_distance_km) + 0.00189 * hypocentral_distance_km + 3.0)


def measure_station_magnitude(job: dict) -> dict:
    day_dir = Path(job["day_dir"])
    station_id = job["station_id"]
    result = {
        "event_index": int(job["event_index"]),
        "station_id": station_id,
        "used_pick": "none",
        "waveform_amplitude_mm": np.nan,
        "fallback_phase_amplitude": float(job["fallback_phase_amplitude"]),
        "station_magnitude": np.nan,
        "status": "missing",
    }
    net, sta = station_id.split(".", 1)
    files = sorted(day_dir.glob(f"{net}.{sta}.*.mseed"))
    if not files:
        result["status"] = "missing_waveform"
        return result
    try:
        stream = read(str(files[0]))
        target_time = None
        pre = None
        post = None
        if job["s_pick_time"] != "-1":
            target_time = UTCDateTime(job["s_pick_time"])
            pre = MAG_WINDOW_PRE_S
            post = MAG_WINDOW_POST_S
            result["used_pick"] = "S"
        elif job["p_pick_time"] != "-1":
            target_time = UTCDateTime(job["p_pick_time"])
            pre = MAG_WINDOW_PRE_P
            post = MAG_WINDOW_POST_P
            result["used_pick"] = "P"
        else:
            result["status"] = "no_pick"
            return result
        trimmed = stream.copy().trim(starttime=target_time - pre, endtime=target_time + post, pad=False)
        horizontal = []
        for tr in trimmed:
            channel = getattr(tr.stats, "channel", "") or ""
            if channel.endswith("E") or channel.endswith("N") or channel.endswith("1") or channel.endswith("2"):
                if tr.stats.npts > 0:
                    horizontal.append(float(np.max(np.abs(tr.data))))
        if horizontal:
            amplitude_mm = max(horizontal) * 1000.0
            result["waveform_amplitude_mm"] = amplitude_mm
            hypo = float(job["hypocentral_distance_km"])
            result["station_magnitude"] = estimate_local_magnitude(amplitude_mm, hypo)
            result["status"] = "ok"
            return result
        result["status"] = "no_horizontal_data"
        return result
    except Exception:
        result["status"] = "error"
        return result


def recompute_event_magnitudes(day_key: str, paired: pd.DataFrame, events_df: pd.DataFrame, stations_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if paired.empty or events_df.empty:
        events_df = events_df.copy()
        events_df["final_magnitude"] = events_df.get("magnitude", np.nan)
        events_df["magnitude_station_count"] = 0
        events_df["magnitude_status"] = "no_event_or_pairs"
        return events_df, pd.DataFrame()
    day_dir = WA_BASE_DIR / day_key
    station_lookup = stations_df.set_index("id").to_dict(orient="index")
    event_lookup = events_df.set_index("event_index").to_dict(orient="index")
    jobs = []
    for row in paired.itertuples(index=False):
        station = station_lookup[row.station_id]
        event = event_lookup[row.event_index]
        epi = haversine_km(event["longitude"], event["latitude"], station["longitude"], station["latitude"])
        depth = float(event["depth_km"])
        station_height = max(0.0, float(station["elevation_m"]) / 1000.0)
        hypo = math.sqrt(epi ** 2 + (depth + station_height) ** 2)
        jobs.append(
            {
                "day_dir": str(day_dir),
                "event_index": int(row.event_index),
                "station_id": row.station_id,
                "p_pick_time": row.p_pick_time,
                "s_pick_time": row.s_pick_time,
                "fallback_phase_amplitude": row.phase_amplitude,
                "hypocentral_distance_km": hypo,
            }
        )
    log(f"[mag:{day_key}] measuring amplitudes for {len(jobs)} event-station pairs with {NCPU} cores")
    results = []
    with ProcessPoolExecutor(max_workers=NCPU) as executor:
        future_map = {executor.submit(measure_station_magnitude, job): job for job in jobs}
        done = 0
        for future in as_completed(future_map):
            try:
                results.append(future.result())
            except Exception as exc:
                job = future_map[future]
                raise RuntimeError(
                    f"Magnitude worker failed for day={day_key}, event_index={job['event_index']}, station_id={job['station_id']}"
                ) from exc
            done += 1
            if done % 100 == 0 or done == len(future_map):
                log(f"[mag:{day_key}] progress {done}/{len(future_map)}")

    station_mag_df = pd.DataFrame(results)
    paired_final = paired.merge(station_mag_df, on=["event_index", "station_id"], how="left")
    paired_final["final_phase_amplitude"] = np.where(
        np.isfinite(paired_final["waveform_amplitude_mm"]),
        paired_final["waveform_amplitude_mm"],
        paired_final["phase_amplitude"],
    )
    event_mag_records = []
    for event_index, group in paired_final.groupby("event_index"):
        valid = group[np.isfinite(group["station_magnitude"])].copy()
        event = event_lookup[event_index]
        if len(valid) >= MIN_STATIONS_FOR_MAG:
            final_mag = float(np.median(valid["station_magnitude"]))
            status = "waveform_median"
        else:
            provisional = event.get("magnitude", np.nan)
            final_mag = float(provisional) if not pd.isna(provisional) else np.nan
            status = "fallback_provisional"
        event_mag_records.append(
            {
                "event_index": int(event_index),
                "final_magnitude": final_mag,
                "magnitude_station_count": int(len(valid)),
                "magnitude_status": status,
            }
        )
    event_mag_df = pd.DataFrame(event_mag_records)
    events_final = events_df.merge(event_mag_df, on="event_index", how="left")
    events_final["final_magnitude"] = np.where(
        np.isfinite(events_final["final_magnitude"]),
        events_final["final_magnitude"],
        events_final.get("magnitude", np.nan),
    )
    events_final["magnitude_station_count"] = events_final["magnitude_station_count"].fillna(0).astype(int)
    events_final["magnitude_status"] = events_final["magnitude_status"].fillna("fallback_provisional")
    return events_final, paired_final


def write_daily_outputs(day_key: str, events_df: pd.DataFrame, paired_df: pd.DataFrame) -> tuple[Path, Path]:
    catalog_path = OUTPUT_DIR / f"catalog_{day_key}.dat"
    phase_path = OUTPUT_DIR / f"phase_{day_key}.dat"
    required_event_cols = ["event_index", "origin_time", "latitude", "longitude", "depth_km", "final_magnitude"]
    missing_event_cols = [col for col in required_event_cols if col not in events_df.columns]
    if missing_event_cols:
        raise ValueError(f"Event table missing required output columns for {day_key}: {missing_event_cols}")
    if not paired_df.empty:
        required_phase_cols = ["event_index", "station_id", "p_pick_time", "s_pick_time", "final_phase_amplitude"]
        missing_phase_cols = [col for col in required_phase_cols if col not in paired_df.columns]
        if missing_phase_cols:
            raise ValueError(f"Paired phase table missing required output columns for {day_key}: {missing_phase_cols}")
    events_sorted = events_df.sort_values("origin_time").reset_index(drop=True)

    with open(catalog_path, "w", encoding="utf-8") as fcat:
        for row in events_sorted.itertuples(index=False):
            line = f"{row.origin_time},{row.latitude:.5f},{row.longitude:.5f},{row.depth_km:.2f},{float(row.final_magnitude):.2f}\n"
            fcat.write(line)
    with open(phase_path, "w", encoding="utf-8") as fpha:
        paired_by_event = defaultdict(list)
        for row in paired_df.itertuples(index=False):
            paired_by_event[int(row.event_index)].append(row)
        for row in events_sorted.itertuples(index=False):
            header = f"{row.origin_time},{row.latitude:.5f},{row.longitude:.5f},{row.depth_km:.2f},{float(row.final_magnitude):.2f}\n"
            fpha.write(header)
            for ph in sorted(paired_by_event.get(int(row.event_index), []), key=lambda x: x.station_id):
                amp = float(ph.final_phase_amplitude) if pd.notna(ph.final_phase_amplitude) else -1.0
                fpha.write(f"{ph.station_id},{ph.p_pick_time},{ph.s_pick_time},{amp}\n")
    log(f"[write:{day_key}] wrote {catalog_path.name} and {phase_path.name}")
    return catalog_path, phase_path


def validate_day_outputs(day_key: str, events_df: pd.DataFrame, paired_df: pd.DataFrame, catalog_path: Path, phase_path: Path, region: dict) -> dict:
    phase_header_count = 0
    with open(phase_path, "r", encoding="utf-8") as fobj:
        for line in fobj:
            if not line.strip():
                continue
            if line.startswith("EVENT,"):
                phase_header_count += 1


    valid_depth = bool(((events_df["depth_km"] >= DEPTH_RANGE_KM[0]) & (events_df["depth_km"] <= DEPTH_RANGE_KM[1])).all()) if len(events_df) else True
    valid_lonlat = bool(
        (
            (events_df["longitude"] >= region["lon_min"] - 1.0)
            & (events_df["longitude"] <= region["lon_max"] + 1.0)
            & (events_df["latitude"] >= region["lat_min"] - 1.0)
            & (events_df["latitude"] <= region["lat_max"] + 1.0)
        ).all()
    ) if len(events_df) else True
    summary = {
        "day": day_key,
        "event_count": int(len(events_df)),
        "phase_rows": int(len(paired_df)),
        "catalog_exists": catalog_path.exists(),
        "phase_exists": phase_path.exists(),
        "phase_header_count": int(phase_header_count),
        "catalog_phase_header_match": int(len(events_df)) == int(phase_header_count),
        "depth_valid": valid_depth,
        "lonlat_valid": valid_lonlat,
    }
    return summary


def plot_association_example(all_paired: pd.DataFrame, all_events: pd.DataFrame, outpath: Path) -> None:
    if all_paired.empty or all_events.empty:
        return
    counts = all_paired.groupby("event_index").size().sort_values(ascending=False)
    event_index = int(counts.index[0])
    event_matches = all_events[all_events["event_index"] == event_index].sort_values("origin_time")
    if event_matches.empty:
        return
    event = event_matches.iloc[0]
    subset = all_paired[all_paired["event_index"] == event_index].copy()

    stations = sorted(subset["station_id"].unique())
    ymap = {sta: i for i, sta in enumerate(stations)}
    fig, ax = plt.subplots(figsize=(11, 6))
    for row in subset.itertuples(index=False):
        if row.p_pick_time != "-1":
            dt = UTCDateTime(row.p_pick_time) - UTCDateTime(event["origin_time"])
            ax.scatter(dt, ymap[row.station_id], c="tab:blue", marker="^", s=50, label="P")
        if row.s_pick_time != "-1":
            dt = UTCDateTime(row.s_pick_time) - UTCDateTime(event["origin_time"])
            ax.scatter(dt, ymap[row.station_id], c="tab:red", marker="o", s=45, label="S")
    handles, labels = ax.get_legend_handles_labels()
    uniq = dict(zip(labels, handles))
    ax.legend(uniq.values(), uniq.keys(), loc="best")
    ax.set_yticks(list(ymap.values()))
    ax.set_yticklabels(list(ymap.keys()))
    ax.set_xlabel("Seconds after event origin time")
    ax.set_ylabel("Station")
    ax.set_title(f"Associated picks example: event {event_index} at {event['origin_time']}")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def plot_event_locations(all_events: pd.DataFrame, stations_df: pd.DataFrame, outpath: Path) -> None:
    if all_events.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    axes[0].scatter(stations_df["longitude"], stations_df["latitude"], c="k", marker="^", s=40, label="Stations")
    sc = axes[0].scatter(all_events["longitude"], all_events["latitude"], c=all_events["depth_km"], cmap="viridis", s=25, label="Events")
    axes[0].set_xlabel("Longitude")
    axes[0].set_ylabel("Latitude")
    axes[0].set_title("Event locations and stations")
    axes[0].legend(loc="best")
    cb = fig.colorbar(sc, ax=axes[0])
    cb.set_label("Depth (km)")
    axes[1].scatter(all_events["longitude"], all_events["depth_km"], c=all_events["final_magnitude"], cmap="plasma", s=25)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Longitude")
    axes[1].set_ylabel("Depth (km)")
    axes[1].set_title("Longitude-depth view")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def plot_event_statistics(all_events: pd.DataFrame, outpath: Path) -> None:
    if all_events.empty:
        return
    event_times = pd.to_datetime(all_events["origin_time"], utc=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    axes[0].hist(event_times, bins=min(24, max(4, len(all_events) // 5 + 1)), color="tab:blue")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].set_title("Event count vs time")
    axes[1].hist(all_events["depth_km"], bins=20, color="tab:green")
    axes[1].set_title("Depth distribution")
    axes[1].set_xlabel("Depth (km)")
    axes[2].hist(all_events["final_magnitude"].dropna(), bins=20, color="tab:orange")
    axes[2].set_title("Magnitude distribution")
    axes[2].set_xlabel("Magnitude")
    fig.tight_layout()
    fig.savefig(outpath, dpi=200)
    plt.close(fig)


def main() -> None:
    log(f"[start] script={SCRIPT_PATH}")
    log(f"[start] output_dir={OUTPUT_DIR}")
    log(f"[start] date_window={START_DATE} to {END_DATE} (processing {PROCESS_DAY_KEYS})")
    log(f"[start] using up to {NCPU} CPU cores")
    ensure_clean_output_dir()
    association_func, gamma_import_name = import_gamma_association()
    log(f"[start] imported GaMMA association from {gamma_import_name}")
    stations_df, proj, region = parse_station_metadata()
    config = build_gamma_config(region)
    all_events = []
    all_paired = []
    qc_pick_rows = []
    validation_rows = []
    for day_key in PROCESS_DAY_KEYS:
        log(f"[day:{day_key}] --------------------------------------------------")
        master_picks, gamma_picks, pick_qc = load_daily_picks(day_key, set(stations_df["id"]))
        qc_pick_rows.append(pick_qc)
        events_df, assignments_df, joined_picks = run_gamma_for_day(
            day_key=day_key,
            master_picks=master_picks,
            gamma_picks=gamma_picks,
            stations=stations_df[["id", "longitude", "latitude", "elevation_m", "x(km)", "y(km)", "z(km)"]].copy(),
            proj=proj,
            config=config.copy(),
            association_func=association_func,
        )
        assignments_out = OUTPUT_DIR / f"assignments_{day_key}.csv"
        joined_out = OUTPUT_DIR / f"assigned_picks_{day_key}.csv"
        events_out = OUTPUT_DIR / f"events_{day_key}.csv"
        assignments_df.to_csv(assignments_out, index=False)
        joined_picks.to_csv(joined_out, index=False)
        events_df.to_csv(events_out, index=False)
        paired_df = pair_event_phases(events_df, joined_picks)
        events_final, paired_final = recompute_event_magnitudes(day_key, paired_df, events_df, stations_df)
        events_final.to_csv(OUTPUT_DIR / f"events_final_{day_key}.csv", index=False)
        paired_final.to_csv(OUTPUT_DIR / f"paired_phases_{day_key}.csv", index=False)
        catalog_path, phase_path = write_daily_outputs(day_key, events_final, paired_final)
        validation_rows.append(validate_day_outputs(day_key, events_final, paired_final, catalog_path, phase_path, region))
        if len(events_final):
            events_final = events_final.copy()
            events_final["day"] = day_key
            all_events.append(events_final)
        if len(paired_final):
            paired_final = paired_final.copy()
            paired_final["day"] = day_key
            all_paired.append(paired_final)
    pick_qc_df = pd.DataFrame(qc_pick_rows)
    validation_df = pd.DataFrame(validation_rows)
    if len(pick_qc_df):
        pick_qc_df.to_csv(OUTPUT_DIR / "pick_qc_summary.csv", index=False)
    if len(validation_df):
        validation_df.to_csv(OUTPUT_DIR / "validation_summary.csv", index=False)
    all_events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    all_paired_df = pd.concat(all_paired, ignore_index=True) if all_paired else pd.DataFrame()
    if len(all_events_df):
        all_events_df.to_csv(OUTPUT_DIR / "all_events_combined.csv", index=False)
    if len(all_paired_df):
        all_paired_df.to_csv(OUTPUT_DIR / "all_paired_phases_combined.csv", index=False)
    plot_association_example(all_paired_df, all_events_df, OUTPUT_DIR / "association_example.png")
    plot_event_locations(all_events_df, stations_df, OUTPUT_DIR / "event_locations.png")
    plot_event_statistics(all_events_df, OUTPUT_DIR / "event_location_statistics.png")
    run_summary = {
        "processed_days": PROCESS_DAY_KEYS,
        "start_date": str(START_DATE),
        "end_date": str(END_DATE),
        "ncpu": NCPU,
        "gamma_method": config["method"],
        "dbscan_eps": DBSCAN_EPS_KM,
        "velocity_model": {
            "z": VELOCITY_DEPTHS_KM,
            "p": VP_KMPS,
            "s": VS_KMPS,
        },
        "magnitude_formula": "ML = log10(A_mm) + 1.11*log10(R_km) + 0.00189*R_km + 3.0",
        "total_events": int(len(all_events_df)),
        "total_phase_rows": int(len(all_paired_df)),
    }
    with open(OUTPUT_DIR / "run_summary.json", "w", encoding="utf-8") as fobj:
        json.dump(run_summary, fobj, indent=2)
    log(f"[done] total events={run_summary['total_events']} total phase rows={run_summary['total_phase_rows']}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
