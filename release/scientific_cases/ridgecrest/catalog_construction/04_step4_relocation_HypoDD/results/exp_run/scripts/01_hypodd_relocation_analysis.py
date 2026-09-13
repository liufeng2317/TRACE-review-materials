import os
import sys
import json
import shutil
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from obspy import UTCDateTime
from torch.utils.data import DataLoader

PAL_HYPODD_ROOT = "<PROJECT_ROOT>/seismoagent/library/basic_fun/PALM/PAL_HypoDD"
if PAL_HYPODD_ROOT not in sys.path:
    sys.path.insert(0, PAL_HYPODD_ROOT)

from pal_hypodd import (
    Config,
    read_fpha,
    mk_sta,
    mk_pha,
    run_ph2dt,
    Run_HypoDD,
    merge_hypodd_output,
    load_hypodd_original_catalog,
    load_hypodd_reloc_catalog,
)

# =========================
# Configuration
# =========================
TASK_NAME = "01_hypodd_relocation_analysis"
OUTPUT_DIR = Path("<CASE_ROOT>/catalog_construction/01_step4_relocation_HypoDD/exp_run/outputs/01_hypodd_relocation_analysis")
SCRIPT_PATH = Path("<CASE_ROOT>/catalog_construction/01_step4_relocation_HypoDD/exp_run/scripts/01_hypodd_relocation_analysis.py")

GAMMA_DIR = Path("<CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude")
STATION_FILE = Path("<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta")
HYPO_ROOT = "<PROJECT_ROOT>/software/hypoDD/HYPODD/src"

DAY_STRINGS = [
    f"201907{day:02d}" for day in range(4, 26)
]
WINDOW_START = UTCDateTime("2019-07-04T00:00:00Z")
WINDOW_END = UTCDateTime("2019-07-26T00:00:00Z")
OT_RANGE = "20190704-20190726"
CATALOG_CODE = "ridgecrest_gamma_20190704_20190726"

LAT_LON_PADDING_DEG = 0.1
KEEP_GRIDS = False
NUM_GRIDS = [1, 1]
XY_PAD = [0.02, 0.02]
NUM_WORKERS = min(4, max(1, (os.cpu_count() or 1) // 2))
DEPTH_CORRECTION_KM = 0.0

# Conservative initial parameters for catalog-only relocation.
PH2DT_PARAMS = {
    "MINWGHT": 0,
    "MAXDIST": 80,
    "MAXSEP": 15,
    "MAXNGH": 10,
    "MINLNK": 4,
    "MINOBS": 4,
    "MAXOBS": 40,
}
HYPO_RELOC_PARAMS = {
    "idat": 2,
    "ipha": 3,
    "dist": 120,
    "obscc": 0,
    "obsct": 8,
}

MAXEVE_LIMIT = 10800
MAXSTA_LIMIT = 1300

PREPARED_PHASE_FILE = OUTPUT_DIR / "prepared_gamma_for_pal_hypodd.pha"
EVENT_MAPPING_FILE = OUTPUT_DIR / "event_id_mapping.csv"
COMBINED_ORIGINAL_CATALOG_FILE = OUTPUT_DIR / "combined_original_catalog.csv"
PHASE_SUMMARY_FILE = OUTPUT_DIR / "phase_pick_summary.csv"
PRECHECK_SUMMARY_FILE = OUTPUT_DIR / "preflight_summary.json"
RELOCATION_MATCH_FILE = OUTPUT_DIR / "matched_original_vs_relocated.csv"
RELOCATION_STATS_FILE = OUTPUT_DIR / "relocation_statistics.json"
RUN_VALIDATION_FILE = OUTPUT_DIR / "run_validation_summary.json"
UNRELOCATED_FILE = OUTPUT_DIR / "unrelocated_events.csv"
RELOCATED_ONLY_FILE = OUTPUT_DIR / "relocated_events.csv"
FIGURE_FILE = OUTPUT_DIR / "hypodd_relocation_comparison.png"


# =========================
# Utilities
# =========================
def log(message: str) -> None:
    print(f"[{UTCDateTime().strftime('%Y-%m-%dT%H:%M:%SZ')}] {message}", flush=True)


def ensure_clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    removable_patterns = [
        "*.npy", "*.loc", "*.reloc", "*.pha", "*.ctlg", "*.res", "*.inp",
        "*.log", "*.csv", "*.json", "*.png", "dt_*.ct", "hypoDD_phase_*.dat", "hypoDD_station.dat"
    ]
    for pattern in removable_patterns:
        for path in output_dir.glob(pattern):
            if path.is_file():
                path.unlink()
    for path in output_dir.iterdir():
        if path.is_dir() and path.name.startswith("grid_"):
            shutil.rmtree(path)


def read_station_metadata(path: Path) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split(",") if part.strip() != ""]
            if len(parts) < 4:
                raise ValueError(f"Malformed station line {lineno}: {line}")
            net_sta = parts[0]
            if "." not in net_sta:
                raise ValueError(f"Station code is not NET.STA at line {lineno}: {line}")
            net, sta = net_sta.split(".", 1)
            rows.append({
                "net_sta": net_sta,
                "network": net,
                "station": sta,
                "latitude": float(parts[1]),
                "longitude": float(parts[2]),
                "elevation_m": float(parts[3]),
                "raw_line": line,
            })
    df = pd.DataFrame(rows).drop_duplicates(subset=["net_sta"]).reset_index(drop=True)
    required_columns = ["net_sta", "network", "station", "latitude", "longitude", "elevation_m"]
    if df.empty:
        raise ValueError("Station metadata is empty.")
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Station metadata missing required columns: {missing_columns}")
    return df


def read_daily_catalog(path: Path, source_day: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["ot", "lat", "lon", "dep", "mag"])
    df["source_day"] = source_day
    df["ot_utc"] = df["ot"].apply(lambda x: UTCDateTime(str(x)))
    return df


def parse_gamma_phase_files(phase_files):
    events = []
    picks = []
    current_event = None
    event_counter = 0

    for phase_file in phase_files:
        source_day = phase_file.stem.split("_")[-1]
        log(f"Parsing phase file: {phase_file}")
        with open(phase_file, "r", encoding="utf-8") as f:
            for lineno, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                record_type = parts[0]
                if record_type == "EVENT":
                    if len(parts) < 6:
                        raise ValueError(f"Malformed EVENT line in {phase_file} line {lineno}: {line}")
                    origin_time = UTCDateTime(parts[1])
                    current_event = {
                        "event_seq": event_counter,
                        "source_day": source_day,
                        "phase_file": str(phase_file),
                        "origin_time": origin_time,
                        "origin_time_str": origin_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "header_time_compact": origin_time.strftime("%Y%m%d%H%M%S.%f")[:-4],
                        "latitude": float(parts[2]),
                        "longitude": float(parts[3]),
                        "depth_km": float(parts[4]),
                        "magnitude": float(parts[5]),
                    }
                    events.append(current_event)
                    event_counter += 1
                elif record_type == "STATION":
                    if current_event is None:
                        raise ValueError(f"STATION line before EVENT in {phase_file} line {lineno}: {line}")
                    if len(parts) < 5:
                        raise ValueError(f"Malformed STATION line in {phase_file} line {lineno}: {line}")
                    net_sta = parts[1]
                    p_pick = parts[2]
                    s_pick = parts[3]
                    picks.append({
                        "event_seq": current_event["event_seq"],
                        "source_day": source_day,
                        "net_sta": net_sta,
                        "p_pick": p_pick,
                        "s_pick": s_pick,
                        "s_amplitude": float(parts[4]),
                        "has_p": p_pick != "-1",
                        "has_s": s_pick != "-1",
                    })
                else:
                    raise ValueError(f"Unknown record type in {phase_file} line {lineno}: {line}")
    events_df = pd.DataFrame(events)
    picks_df = pd.DataFrame(picks)
    return events_df, picks_df


def filter_window(events_df: pd.DataFrame, picks_df: pd.DataFrame):
    mask = events_df["origin_time"].apply(lambda t: WINDOW_START <= t < WINDOW_END)
    events_df = events_df.loc[mask].copy().reset_index(drop=True)
    valid_ids = set(events_df["event_seq"].tolist())
    picks_df = picks_df[picks_df["event_seq"].isin(valid_ids)].copy().reset_index(drop=True)
    return events_df, picks_df


def build_prepared_phase_file(events_df: pd.DataFrame, picks_df: pd.DataFrame, out_path: Path):
    events_df = events_df.sort_values("origin_time").reset_index(drop=True).copy()
    events_df["event_id"] = np.arange(len(events_df), dtype=int)
    event_id_map = dict(zip(events_df["event_seq"], events_df["event_id"]))
    picks_df = picks_df.copy()
    picks_df["event_id"] = picks_df["event_seq"].map(event_id_map)
    picks_df = picks_df.sort_values(["event_id", "net_sta"]).reset_index(drop=True)

    picks_by_event = {eid: grp for eid, grp in picks_df.groupby("event_id", sort=True)}
    phase_summary_rows = []
    with open(out_path, "w", encoding="utf-8") as f:
        for row in events_df.itertuples(index=False):
            event_picks = picks_by_event.get(row.event_id)
            if event_picks is None or event_picks.empty:
                continue
            valid_pick_rows = event_picks[(event_picks["has_p"]) | (event_picks["has_s"])].copy()
            if valid_pick_rows.empty:
                continue
            header = (
                f"{row.header_time_compact},{row.latitude:.5f},{row.longitude:.5f},"
                f"{row.depth_km:.2f},{row.magnitude:.2f},{int(row.event_id)}\n"
            )
            f.write(header)
            for prow in valid_pick_rows.itertuples(index=False):
                f.write(f"{prow.net_sta},{prow.p_pick},{prow.s_pick}\n")
            phase_summary_rows.append({
                "event_id": int(row.event_id),
                "event_seq": int(row.event_seq),
                "source_day": row.source_day,
                "origin_time": row.origin_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "n_station_rows": int(len(valid_pick_rows)),
                "n_picks_p": int(valid_pick_rows["has_p"].sum()),
                "n_picks_s": int(valid_pick_rows["has_s"].sum()),
            })

    events_df["event_id"] = events_df["event_id"].astype(int)
    phase_summary_df = pd.DataFrame(phase_summary_rows)
    if "event_id" not in picks_df.columns:
        raise ValueError("Prepared picks table is missing event_id after event-id mapping.")
    return events_df, picks_df, phase_summary_df


def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
    c = 2.0 * np.arcsin(np.sqrt(a))
    return radius_km * c


def summarize_catalog(df: pd.DataFrame, prefix: str):
    return {
        f"{prefix}_count": int(len(df)),
        f"{prefix}_lat_min": float(df["lat"].min()) if len(df) else None,
        f"{prefix}_lat_max": float(df["lat"].max()) if len(df) else None,
        f"{prefix}_lon_min": float(df["lon"].min()) if len(df) else None,
        f"{prefix}_lon_max": float(df["lon"].max()) if len(df) else None,
        f"{prefix}_dep_min": float(df["dep"].min()) if len(df) else None,
        f"{prefix}_dep_max": float(df["dep"].max()) if len(df) else None,
    }


def match_catalogs_by_nearest_time(original_df: pd.DataFrame, reloc_df: pd.DataFrame, tolerance_seconds: float = 10.0) -> pd.DataFrame:
    required_original = ["event_id", "original_ot", "original_ot_str", "original_lat", "original_lon", "original_dep", "original_mag"]
    required_reloc = ["ot", "lat", "lon", "dep", "mag"]
    missing_original = [col for col in required_original if col not in original_df.columns]
    missing_reloc = [col for col in required_reloc if col not in reloc_df.columns]
    if missing_original:
        raise ValueError(f"Original table missing required columns for nearest-time matching: {missing_original}")
    if missing_reloc:
        raise ValueError(f"Relocated catalog missing required columns for nearest-time matching: {missing_reloc}")

    available = reloc_df.copy().sort_values("ot").reset_index(drop=True)
    available["used"] = False
    matched_rows = []

    for row in original_df.sort_values("original_ot").itertuples(index=False):
        unused = available.loc[~available["used"]].copy()
        if unused.empty:
            break
        dt_seconds = unused["ot"].apply(lambda t: abs(t - row.original_ot))
        best_idx = dt_seconds.idxmin()
        best_dt = float(dt_seconds.loc[best_idx])
        if best_dt <= tolerance_seconds:
            best = available.loc[best_idx]
            available.loc[best_idx, "used"] = True
            matched_rows.append({
                "event_id": int(row.event_id),
                "event_seq": int(row.event_seq),
                "source_day": row.source_day,
                "phase_file": row.phase_file,
                "original_ot_str": row.original_ot_str,
                "original_lat": float(row.original_lat),
                "original_lon": float(row.original_lon),
                "original_dep": float(row.original_dep),
                "original_mag": float(row.original_mag),
                "reloc_ot_str": best["ot"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "reloc_lat": float(best["lat"]),
                "reloc_lon": float(best["lon"]),
                "reloc_dep": float(best["dep"]),
                "reloc_mag": float(best["mag"]),
                "origin_time_abs_diff_s": best_dt,
            })
    return pd.DataFrame(matched_rows)


def require_file_nonempty(path: Path, description: str):
    if not path.is_file():
        raise FileNotFoundError(f"Missing {description}: {path}")
    if path.stat().st_size == 0:
        raise RuntimeError(f"Empty {description}: {path}")


def save_json(path: Path, payload: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def make_comparison_figure(stations_df, original_df, relocated_df, matched_df, summary_counts, out_path):
    required_original_cols = ["lon", "lat", "dep", "mag", "ot"]
    required_reloc_cols = ["lon", "lat", "dep", "mag", "ot"]
    required_match_cols = [
        "original_lon", "original_lat", "original_dep",
        "reloc_lon", "reloc_lat", "reloc_dep", "horizontal_shift_km"
    ]
    for cols, df_name, df in [
        (required_original_cols, "original_df", original_df),
        (required_reloc_cols, "relocated_df", relocated_df),
        (required_match_cols, "matched_df", matched_df),
    ]:
        missing = [col for col in cols if col not in df.columns]
        if missing:
            raise ValueError(f"{df_name} missing required columns for plotting: {missing}")
    lon_min = min(stations_df["longitude"].min(), original_df["lon"].min(), relocated_df["lon"].min()) - 0.03
    lon_max = max(stations_df["longitude"].max(), original_df["lon"].max(), relocated_df["lon"].max()) + 0.03
    lat_min = min(stations_df["latitude"].min(), original_df["lat"].min(), relocated_df["lat"].min()) - 0.03
    lat_max = max(stations_df["latitude"].max(), original_df["lat"].max(), relocated_df["lat"].max()) + 0.03

    fig = plt.figure(figsize=(18, 14), constrained_layout=True)
    gs = GridSpec(3, 3, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])
    ax4 = fig.add_subplot(gs[1, 0])
    ax5 = fig.add_subplot(gs[1, 1])
    ax6 = fig.add_subplot(gs[1, 2])
    ax7 = fig.add_subplot(gs[2, :])

    station_style = dict(marker="^", s=45, color="black", alpha=0.85, label="Stations")

    ax1.scatter(original_df["lon"], original_df["lat"], s=6, c="tab:blue", alpha=0.55, label="Original")
    ax1.scatter(stations_df["longitude"], stations_df["latitude"], **station_style)
    ax1.set_title("Original Gamma epicenters")

    ax2.scatter(relocated_df["lon"], relocated_df["lat"], s=6, c="tab:red", alpha=0.55, label="Relocated")
    ax2.scatter(stations_df["longitude"], stations_df["latitude"], **station_style)
    ax2.set_title("Relocated HypoDD epicenters")

    ax3.scatter(original_df["lon"], original_df["lat"], s=6, c="tab:blue", alpha=0.35, label="Original")
    ax3.scatter(relocated_df["lon"], relocated_df["lat"], s=6, c="tab:red", alpha=0.35, label="Relocated")
    ax3.scatter(stations_df["longitude"], stations_df["latitude"], **station_style)
    for _, row in matched_df.iloc[::max(1, len(matched_df)//400)].iterrows():
        ax3.plot([row["original_lon"], row["reloc_lon"]], [row["original_lat"], row["reloc_lat"]], color="gray", alpha=0.15, linewidth=0.4)
    ax3.set_title("Original vs relocated overlay")
    ax3.legend(loc="best", fontsize=8)

    ax4.scatter(matched_df["original_lon"], matched_df["original_dep"], s=6, c="tab:blue", alpha=0.35, label="Original")
    ax4.scatter(matched_df["reloc_lon"], matched_df["reloc_dep"], s=6, c="tab:red", alpha=0.35, label="Relocated")
    ax4.invert_yaxis()
    ax4.set_title("Longitude-depth comparison")
    ax4.set_xlabel("Longitude")
    ax4.set_ylabel("Depth (km)")
    ax4.legend(loc="best", fontsize=8)

    ax5.scatter(matched_df["original_lat"], matched_df["original_dep"], s=6, c="tab:blue", alpha=0.35, label="Original")
    ax5.scatter(matched_df["reloc_lat"], matched_df["reloc_dep"], s=6, c="tab:red", alpha=0.35, label="Relocated")
    ax5.invert_yaxis()
    ax5.set_title("Latitude-depth comparison")
    ax5.set_xlabel("Latitude")
    ax5.set_ylabel("Depth (km)")
    ax5.legend(loc="best", fontsize=8)

    ax6.hist(matched_df["horizontal_shift_km"], bins=40, color="tab:purple", alpha=0.85)
    ax6.set_title("Horizontal relocation distance")
    ax6.set_xlabel("Shift (km)")
    ax6.set_ylabel("Count")

    ax7.axis("off")
    summary_lines = [
        "HypoDD relocation summary",
        f"Window: {WINDOW_START} to {WINDOW_END}",
        f"Original events in window: {summary_counts['n_original_events']}",
        f"Prepared phase events: {summary_counts['n_phase_events']}",
        f"Events selected into HypoDD grids: {summary_counts['n_selected_events']}",
        f"Relocated events: {summary_counts['n_relocated_events']}",
        f"Relocation success rate: {summary_counts['relocation_success_rate_percent']:.2f}%",
        f"Median horizontal shift: {summary_counts['horizontal_shift_median_km']:.3f} km",
        f"Mean horizontal shift: {summary_counts['horizontal_shift_mean_km']:.3f} km",
        f"Max horizontal shift: {summary_counts['horizontal_shift_max_km']:.3f} km",
        f"Median depth change: {summary_counts['depth_change_median_km']:.3f} km",
        f"Station count: {summary_counts['n_stations']}",
        "Blue = original Gamma catalog, Red = relocated HypoDD catalog",
    ]
    ax7.text(0.01, 0.98, "\n".join(summary_lines), va="top", ha="left", fontsize=12, family="monospace")

    for ax in [ax1, ax2, ax3]:
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True, alpha=0.25)
    for ax in [ax4, ax5, ax6]:
        ax.grid(True, alpha=0.25)

    fig.suptitle("Ridgecrest 2019-07-04 to 2019-07-26: original Gamma vs relocated HypoDD catalog", fontsize=16)
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def main():
    log(f"Starting task: {TASK_NAME}")
    ensure_clean_output_dir(OUTPUT_DIR)

    log("Step 1/10: checking required executables and input files")
    ph2dt_exe = Path(HYPO_ROOT) / "ph2dt" / "ph2dt"
    hypodd_exe = Path(HYPO_ROOT) / "hypoDD" / "hypoDD"
    require_file_nonempty(ph2dt_exe, "ph2dt executable")
    require_file_nonempty(hypodd_exe, "hypoDD executable")
    require_file_nonempty(STATION_FILE, "station metadata file")
    phase_files = [GAMMA_DIR / f"phase_{day}.dat" for day in DAY_STRINGS]
    catalog_files = [GAMMA_DIR / f"catalog_{day}.dat" for day in DAY_STRINGS]
    for p in phase_files + catalog_files:
        require_file_nonempty(p, f"input file {p.name}")

    log("Step 2/10: loading station metadata and deriving relocation bounds")
    stations_df = read_station_metadata(STATION_FILE)
    lat_range = [float(stations_df["latitude"].min() - LAT_LON_PADDING_DEG), float(stations_df["latitude"].max() + LAT_LON_PADDING_DEG)]
    lon_range = [float(stations_df["longitude"].min() - LAT_LON_PADDING_DEG), float(stations_df["longitude"].max() + LAT_LON_PADDING_DEG)]
    log(f"Station count = {len(stations_df)}")
    log(f"Derived lat_range = {lat_range}")
    log(f"Derived lon_range = {lon_range}")

    log("Step 3/10: reading full-window Gamma catalog and phase products")
    catalog_df = pd.concat([read_daily_catalog(path, day) for path, day in zip(catalog_files, DAY_STRINGS)], ignore_index=True)
    events_df, picks_df = parse_gamma_phase_files(phase_files)
    events_df, picks_df = filter_window(events_df, picks_df)
    catalog_df = catalog_df[catalog_df["ot_utc"].apply(lambda t: WINDOW_START <= t < WINDOW_END)].copy().reset_index(drop=True)
    catalog_df.to_csv(COMBINED_ORIGINAL_CATALOG_FILE, index=False)
    log(f"Catalog events in requested window = {len(catalog_df)}")
    log(f"Phase EVENT blocks in requested window = {len(events_df)}")
    log(f"Total station-phase rows in requested window = {len(picks_df)}")

    log("Step 4/10: validating station consistency and preparing PAL_HypoDD phase input")
    station_set = set(stations_df["net_sta"].tolist())
    pick_station_set = set(picks_df["net_sta"].tolist())
    missing_stations = sorted(pick_station_set - station_set)
    if missing_stations:
        raise ValueError(f"Stations present in phase picks but absent from station metadata: {missing_stations[:20]}")

    events_with_ids_df, prepared_picks_df, phase_summary_df = build_prepared_phase_file(events_df, picks_df, PREPARED_PHASE_FILE)
    if phase_summary_df.empty:
        raise RuntimeError("Prepared phase summary is empty; no events retained for HypoDD input.")
    phase_summary_df.to_csv(PHASE_SUMMARY_FILE, index=False)
    mapping_df = events_with_ids_df[["event_id", "event_seq", "source_day", "origin_time_str", "latitude", "longitude", "depth_km", "magnitude", "phase_file"]].copy()
    mapping_df.to_csv(EVENT_MAPPING_FILE, index=False)
    log(f"Prepared phase file written: {PREPARED_PHASE_FILE}")
    log(f"Prepared phase events retained = {len(mapping_df)}")

    log("Step 5/10: validating prepared phase parsing and preflight counts")
    pha_dict, mag_dict = read_fpha(str(PREPARED_PHASE_FILE))
    if len(pha_dict) == 0:
        raise RuntimeError("Prepared phase file parsed to zero events.")
    if len(pha_dict) > MAXEVE_LIMIT:
        raise RuntimeError(f"Prepared event count {len(pha_dict)} exceeds HypoDD MAXEVE limit {MAXEVE_LIMIT}.")
    if len(stations_df) > MAXSTA_LIMIT:
        raise RuntimeError(f"Station count {len(stations_df)} exceeds HypoDD MAXSTA limit {MAXSTA_LIMIT}.")

    n_p_picks = int(prepared_picks_df["has_p"].sum())
    n_s_picks = int(prepared_picks_df["has_s"].sum())
    preflight = {
        "window_start": str(WINDOW_START),
        "window_end": str(WINDOW_END),
        "n_stations": int(len(stations_df)),
        "n_original_events": int(len(catalog_df)),
        "n_phase_events": int(len(events_with_ids_df)),
        "n_pick_rows": int(len(prepared_picks_df)),
        "n_p_picks": n_p_picks,
        "n_s_picks": n_s_picks,
        "lat_range": lat_range,
        "lon_range": lon_range,
        "keep_grids": KEEP_GRIDS,
        "num_grids": NUM_GRIDS,
        "xy_pad": XY_PAD,
        "num_workers": NUM_WORKERS,
        "ph2dt_params": PH2DT_PARAMS,
        "hypo_reloc_params": HYPO_RELOC_PARAMS,
    }
    save_json(PRECHECK_SUMMARY_FILE, preflight)
    log(json.dumps(preflight, indent=2))

    log("Step 6/10: building PAL_HypoDD config and generating HypoDD station/phase files")
    cfg = Config(
        hypo_root=HYPO_ROOT,
        ctlg_code=CATALOG_CODE,
        fsta=str(STATION_FILE),
        fpha=str(PREPARED_PHASE_FILE),
        dep_corr=DEPTH_CORRECTION_KM,
        ot_range=OT_RANGE,
        lat_range=lat_range,
        lon_range=lon_range,
        num_grids=NUM_GRIDS,
        xy_pad=XY_PAD,
        num_workers=NUM_WORKERS,
        keep_grids=KEEP_GRIDS,
        hypoDD_reloc_params=HYPO_RELOC_PARAMS,
        ph2dt_params=PH2DT_PARAMS,
    )
    mk_sta(cfg.fsta, str(OUTPUT_DIR))
    mk_pha(cfg.fpha, str(OUTPUT_DIR), cfg)
    evid_lists = np.load(OUTPUT_DIR / "evid_lists.npy", allow_pickle=True)
    selected_events = []
    for i in range(cfg.num_grids[0]):
        for j in range(cfg.num_grids[1]):
            selected_events.extend(list(evid_lists[i][j]))
    selected_event_ids = sorted({int(v) for v in selected_events})
    if len(selected_event_ids) == 0:
        raise RuntimeError("mk_pha selected zero events; fix ot_range/lat_range/lon_range or phase parsing.")
    log(f"Events selected into HypoDD grid files = {len(selected_event_ids)}")

    log("Step 7/10: running ph2dt to generate differential times")
    run_ph2dt(str(OUTPUT_DIR), cfg)
    dt_files = sorted(OUTPUT_DIR.glob("dt_*.ct"))
    if not dt_files:
        raise RuntimeError("ph2dt did not create any dt_*.ct files.")
    for path in dt_files:
        require_file_nonempty(path, f"differential-time file {path.name}")
    log(f"Generated {len(dt_files)} differential-time files")

    log("Step 8/10: running HypoDD relocation")
    idx_list = [(i, j) for i in range(cfg.num_grids[0]) for j in range(cfg.num_grids[1])]
    dataset = Run_HypoDD(evid_lists, idx_list, pha_dict, mag_dict, str(OUTPUT_DIR), cfg)
    for _ in DataLoader(dataset, num_workers=cfg.num_workers, batch_size=None):
        pass
    merge_hypodd_output(cfg.ctlg_code, str(OUTPUT_DIR), keep_grids=cfg.keep_grids)

    original_loc_file = OUTPUT_DIR / f"{CATALOG_CODE}.loc"
    reloc_file = OUTPUT_DIR / f"{CATALOG_CODE}.reloc"
    merged_phase_file = OUTPUT_DIR / f"{CATALOG_CODE}.pha"
    require_file_nonempty(original_loc_file, "merged original location catalog")
    require_file_nonempty(reloc_file, "merged relocated catalog")
    require_file_nonempty(merged_phase_file, "merged HypoDD phase file")
    ph2dt_log = OUTPUT_DIR / "ph2dt.log"
    hypodd_log = OUTPUT_DIR / "hypoDD.log"
    require_file_nonempty(ph2dt_log, "ph2dt log")
    require_file_nonempty(hypodd_log, "hypoDD log")

    log("Step 9/10: loading relocation outputs and computing statistics")
    hypodd_original_df = load_hypodd_original_catalog(CATALOG_CODE, str(OUTPUT_DIR)).copy()
    hypodd_reloc_df = load_hypodd_reloc_catalog(CATALOG_CODE, str(OUTPUT_DIR)).copy()
    if hypodd_original_df.empty:
        raise RuntimeError("Original HypoDD catalog is empty.")
    if hypodd_reloc_df.empty:
        raise RuntimeError("Relocated catalog is empty.")

    for required_col in ["ot", "lat", "lon", "dep", "mag"]:
        if required_col not in hypodd_original_df.columns:
            raise ValueError(f"Original HypoDD catalog missing required column: {required_col}")
        if required_col not in hypodd_reloc_df.columns:
            raise ValueError(f"Relocated HypoDD catalog missing required column: {required_col}")

    hypodd_original_df["ot_str"] = hypodd_original_df["ot"].apply(lambda t: t.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    hypodd_reloc_df["ot_str"] = hypodd_reloc_df["ot"].apply(lambda t: t.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))

    mapping_df = pd.read_csv(EVENT_MAPPING_FILE)
    mapping_df = mapping_df.rename(columns={
        "origin_time_str": "original_ot_str",
        "latitude": "original_lat",
        "longitude": "original_lon",
        "depth_km": "original_dep",
        "magnitude": "original_mag",
    })
    required_mapping_cols = ["event_id", "event_seq", "source_day", "phase_file", "original_ot_str", "original_lat", "original_lon", "original_dep", "original_mag"]
    missing_mapping_cols = [col for col in required_mapping_cols if col not in mapping_df.columns]
    if missing_mapping_cols:
        raise ValueError(f"Event mapping table missing required columns: {missing_mapping_cols}")
    mapping_df["original_ot"] = mapping_df["original_ot_str"].apply(lambda x: UTCDateTime(x))
    mapping_df["was_selected"] = mapping_df["event_id"].isin(selected_event_ids)

    matched_original_df = match_catalogs_by_nearest_time(
        mapping_df.loc[mapping_df["was_selected"]].copy(),
        hypodd_original_df.copy(),
        tolerance_seconds=10.0,
    )
    if matched_original_df.empty:
        raise RuntimeError("Failed to match selected input events to HypoDD original catalog by nearest origin time.")
    matched_original_df = matched_original_df.rename(columns={
        "reloc_ot_str": "hypodd_original_ot_str",
        "reloc_lat": "hypodd_original_lat",
        "reloc_lon": "hypodd_original_lon",
        "reloc_dep": "hypodd_original_dep",
        "reloc_mag": "hypodd_original_mag",
        "origin_time_abs_diff_s": "hypodd_original_time_abs_diff_s",
    })
    matched_original_df = matched_original_df[[
        "event_id", "hypodd_original_ot_str", "hypodd_original_lat", "hypodd_original_lon",
        "hypodd_original_dep", "hypodd_original_mag", "hypodd_original_time_abs_diff_s"
    ]]

    matched_reloc_df = match_catalogs_by_nearest_time(
        mapping_df.loc[mapping_df["was_selected"]].copy(),
        hypodd_reloc_df.copy(),
        tolerance_seconds=10.0,
    )
    if matched_reloc_df.empty:
        raise RuntimeError("Failed to match selected input events to relocated HypoDD catalog by nearest origin time.")

    matched_df = mapping_df.merge(matched_original_df, on="event_id", how="left")
    matched_df = matched_df.merge(
        matched_reloc_df[["event_id", "reloc_ot_str", "reloc_lat", "reloc_lon", "reloc_dep", "reloc_mag", "origin_time_abs_diff_s"]],
        on="event_id", how="left"
    )
    matched_df = matched_df.rename(columns={"origin_time_abs_diff_s": "reloc_time_abs_diff_s"})
    matched_df["was_relocated"] = matched_df["reloc_lat"].notna()
    relocated_only = matched_df[matched_df["was_relocated"]].copy()
    if relocated_only.empty:
        raise RuntimeError("No matched relocated events were found after nearest-time catalog matching.")

    relocated_only["horizontal_shift_km"] = haversine_km(
        relocated_only["original_lat"].to_numpy(),
        relocated_only["original_lon"].to_numpy(),
        relocated_only["reloc_lat"].to_numpy(),
        relocated_only["reloc_lon"].to_numpy(),
    )
    relocated_only["depth_change_km"] = relocated_only["reloc_dep"] - relocated_only["original_dep"]
    relocated_only["day"] = relocated_only["original_ot_str"].str.slice(0, 10)

    matched_df = matched_df.merge(
        relocated_only[["event_id", "horizontal_shift_km", "depth_change_km", "day"]],
        on="event_id", how="left"
    )
    matched_df.to_csv(RELOCATION_MATCH_FILE, index=False)
    relocated_only.to_csv(RELOCATED_ONLY_FILE, index=False)
    matched_df.loc[matched_df["was_selected"] & ~matched_df["was_relocated"]].to_csv(UNRELOCATED_FILE, index=False)

    by_day_counts = {
        day: int((relocated_only["day"] == day).sum())
        for day in sorted(relocated_only["day"].dropna().unique())
    }
    original_catalog_for_plot = catalog_df.rename(columns={"ot": "ot_str", "lat": "lat", "lon": "lon", "dep": "dep", "mag": "mag"})[["ot_str", "lat", "lon", "dep", "mag"]].copy()
    required_plot_cols = ["ot_str", "lat", "lon", "dep", "mag"]
    missing_plot_cols = [col for col in required_plot_cols if col not in original_catalog_for_plot.columns]
    if missing_plot_cols:
        raise ValueError(f"Original catalog plot table missing required columns: {missing_plot_cols}")
    original_catalog_for_plot["ot"] = original_catalog_for_plot["ot_str"].apply(lambda x: UTCDateTime(x))

    summary_stats = {
        "n_stations": int(len(stations_df)),
        "n_original_events": int(len(catalog_df)),
        "n_phase_events": int(len(events_with_ids_df)),
        "n_selected_events": int(len(selected_event_ids)),
        "n_hypodd_original_catalog_events": int(len(hypodd_original_df)),
        "n_hypodd_relocated_catalog_events": int(len(hypodd_reloc_df)),
        "n_relocated_events": int(len(relocated_only)),
        "relocation_success_rate_percent": float(100.0 * len(relocated_only) / max(1, len(selected_event_ids))),
        "matching_method": "nearest_origin_time_unique_match",
        "matching_tolerance_seconds": 10.0,
        "horizontal_shift_mean_km": float(relocated_only["horizontal_shift_km"].mean()),
        "horizontal_shift_median_km": float(relocated_only["horizontal_shift_km"].median()),
        "horizontal_shift_max_km": float(relocated_only["horizontal_shift_km"].max()),
        "horizontal_shift_p95_km": float(relocated_only["horizontal_shift_km"].quantile(0.95)),
        "depth_change_mean_km": float(relocated_only["depth_change_km"].mean()),
        "depth_change_median_km": float(relocated_only["depth_change_km"].median()),
        "reloc_time_abs_diff_mean_s": float(relocated_only["reloc_time_abs_diff_s"].mean()),
        "reloc_time_abs_diff_median_s": float(relocated_only["reloc_time_abs_diff_s"].median()),
        "counts_by_day_relocated": by_day_counts,
    }
    summary_stats.update(summarize_catalog(original_catalog_for_plot.rename(columns={"ot_str": "ot"}), "original_catalog"))
    summary_stats.update(summarize_catalog(hypodd_reloc_df, "relocated_catalog"))
    save_json(RELOCATION_STATS_FILE, summary_stats)

    run_validation = {
        "task_name": TASK_NAME,
        "window_start": str(WINDOW_START),
        "window_end": str(WINDOW_END),
        "native_execution_confirmed": True,
        "ph2dt_log_exists": ph2dt_log.is_file(),
        "hypodd_log_exists": hypodd_log.is_file(),
        "ph2dt_log_bytes": ph2dt_log.stat().st_size,
        "hypodd_log_bytes": hypodd_log.stat().st_size,
        "prepared_phase_file": str(PREPARED_PHASE_FILE),
        "original_loc_file": str(original_loc_file),
        "reloc_file": str(reloc_file),
        "figure_file": str(FIGURE_FILE),
        "matching_method": summary_stats["matching_method"],
        "matching_tolerance_seconds": summary_stats["matching_tolerance_seconds"],
        "n_original_events": summary_stats["n_original_events"],
        "n_selected_events": summary_stats["n_selected_events"],
        "n_hypodd_original_catalog_events": summary_stats["n_hypodd_original_catalog_events"],
        "n_hypodd_relocated_catalog_events": summary_stats["n_hypodd_relocated_catalog_events"],
        "n_relocated_events": summary_stats["n_relocated_events"],
        "relocation_success_rate_percent": summary_stats["relocation_success_rate_percent"],
        "horizontal_shift_median_km": summary_stats["horizontal_shift_median_km"],
        "horizontal_shift_mean_km": summary_stats["horizontal_shift_mean_km"],
        "horizontal_shift_p95_km": summary_stats["horizontal_shift_p95_km"],
        "result_quality_note": "This run executed native ph2dt and hypoDD, produced non-empty loc/reloc catalogs, and computed matched relocation statistics from real outputs.",
    }
    save_json(RUN_VALIDATION_FILE, run_validation)
    log(json.dumps(summary_stats, indent=2))
    log(json.dumps(run_validation, indent=2))

    log("Step 10/10: generating comparison figure")
    plot_original_df = original_catalog_for_plot[["lon", "lat", "dep", "mag", "ot"]].copy()
    plot_reloc_df = hypodd_reloc_df[["lon", "lat", "dep", "mag", "ot"]].copy()
    make_comparison_figure(stations_df, plot_original_df, plot_reloc_df, relocated_only, summary_stats, FIGURE_FILE)
    require_file_nonempty(FIGURE_FILE, "final comparison figure")
    log(f"Finished successfully. Outputs saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
