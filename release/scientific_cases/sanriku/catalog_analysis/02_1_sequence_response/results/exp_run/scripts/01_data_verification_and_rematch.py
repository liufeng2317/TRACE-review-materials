from __future__ import annotations

import json
import math
import shutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch")

CATALOG_PATH = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MAIN_PATH = BASE_DIR / "catalog/main_earthquake.csv"
MECHA_PATH = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_PATH = BASE_DIR / "stations/station.sta"

TIME_TOLERANCE_SEC = 3600.0  # allow relocation-induced shifts within 1 hour
MAX_CANDIDATES = 10
MATCH_DISTANCE_KM_SOFT = 80.0
OUTPUT_STALE_PATTERNS = [
    "*.csv",
    "*.json",
    "*.png",
    "*.jpg",
    "*.jpeg",
]


@dataclass
class MainshockMatch:
    label: str
    ref_datetime: pd.Timestamp
    ref_lat: float
    ref_lon: float
    ref_dep: float
    ref_mag: float
    matched_index: Optional[int]
    matched_datetime: Optional[pd.Timestamp]
    matched_lat: Optional[float]
    matched_lon: Optional[float]
    matched_dep: Optional[float]
    matched_mag: Optional[float]
    time_diff_sec: Optional[float]
    horizontal_distance_km: Optional[float]
    depth_diff_km: Optional[float]
    combined_score: Optional[float]
    n_close_candidates: int
    candidate_preview: str
    match_status: str


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


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * 6371.0 * np.arcsin(np.sqrt(a))


def parse_time_series(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce", utc=True)


def verify_catalog(df: pd.DataFrame, path: Path) -> Dict[str, object]:
    required = ["datetime", "lat", "lon", "dep", "mag"]
    missing = [c for c in required if c not in df.columns]
    out = {
        "path": str(path),
        "n_rows": int(len(df)),
        "columns": list(df.columns),
        "required_fields_present": len(missing) == 0,
        "missing_required_fields": missing,
        "time_parse_missing": int(df["datetime"].isna().sum()) if "datetime" in df.columns else None,
        "lat_missing": int(df["lat"].isna().sum()) if "lat" in df.columns else None,
        "lon_missing": int(df["lon"].isna().sum()) if "lon" in df.columns else None,
        "dep_missing": int(df["dep"].isna().sum()) if "dep" in df.columns else None,
        "mag_missing": int(df["mag"].isna().sum()) if "mag" in df.columns else None,
    }
    return out


def verify_main(df: pd.DataFrame, path: Path) -> Dict[str, object]:
    required = ["index", "datetime", "lat", "lon", "dep", "mag"]
    missing = [c for c in required if c not in df.columns]
    return {
        "path": str(path),
        "n_rows": int(len(df)),
        "columns": list(df.columns),
        "required_fields_present": len(missing) == 0,
        "missing_required_fields": missing,
    }


def verify_mecha(df: pd.DataFrame, path: Path) -> Dict[str, object]:
    required = ["event_code", "origin_time", "lat_deg", "lon_deg", "depth_km", "mag_1"]
    missing = [c for c in required if c not in df.columns]
    coverage_cols = [c for c in ["focal_mech_score", "n_mech_stations", "strike_plane1", "dip_plane1", "rake_plane1"] if c in df.columns]
    coverage = {}
    for c in coverage_cols:
        coverage[c] = int(df[c].notna().sum())
    return {
        "path": str(path),
        "n_rows": int(len(df)),
        "columns": list(df.columns),
        "required_fields_present": len(missing) == 0,
        "missing_required_fields": missing,
        "non_missing_counts": coverage,
    }


def verify_station(df: pd.DataFrame, path: Path) -> Dict[str, object]:
    required_any = ["station_code", "station_number", "latitude", "longitude"]
    missing = [c for c in required_any if c not in df.columns]
    return {
        "path": str(path),
        "n_rows": int(len(df)),
        "columns": list(df.columns),
        "required_fields_present": len(missing) == 0,
        "missing_required_fields": missing,
    }


def build_candidates(main_row: pd.Series, cat: pd.DataFrame) -> pd.DataFrame:
    dt_ref = main_row["datetime"]
    dt_diff = (cat["datetime"] - dt_ref).dt.total_seconds().abs()
    tmask = dt_diff <= TIME_TOLERANCE_SEC
    if not tmask.any():
        tmask = dt_diff <= 6 * 3600
    sub = cat.loc[tmask].copy()
    sub["time_diff_sec"] = (sub["datetime"] - dt_ref).dt.total_seconds()
    sub["abs_time_diff_sec"] = sub["time_diff_sec"].abs()
    sub["horizontal_distance_km"] = haversine_km(main_row["lat"], main_row["lon"], sub["lat"].to_numpy(), sub["lon"].to_numpy())
    sub["depth_diff_km"] = (sub["dep"] - main_row["dep"]).abs()
    sub["combined_score"] = sub["abs_time_diff_sec"] / 60.0 + sub["horizontal_distance_km"] + 0.2 * sub["depth_diff_km"]
    sub = sub.sort_values(["combined_score", "abs_time_diff_sec", "horizontal_distance_km", "depth_diff_km"])
    return sub


def match_mainshocks(main_df: pd.DataFrame, cat_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    matches = []
    previews = []
    for _, row in main_df.iterrows():
        cands = build_candidates(row, cat_df)
        n_close = int(len(cands))
        best = cands.iloc[0] if len(cands) else None
        if best is not None:
            status = "matched" if (abs(best["time_diff_sec"]) <= TIME_TOLERANCE_SEC or best["horizontal_distance_km"] <= MATCH_DISTANCE_KM_SOFT) else "weak_match"
            preview_df = cands.head(MAX_CANDIDATES)[["datetime", "lat", "lon", "dep", "mag", "time_diff_sec", "horizontal_distance_km", "depth_diff_km", "combined_score"]].copy()
            previews.append({"mainshock": row["index"], "candidates_preview": preview_df.to_dict(orient="records")})
            matches.append(MainshockMatch(
                label=row["index"],
                ref_datetime=row["datetime"],
                ref_lat=float(row["lat"]),
                ref_lon=float(row["lon"]),
                ref_dep=float(row["dep"]),
                ref_mag=float(row["mag"]),
                matched_index=int(best.name),
                matched_datetime=best["datetime"],
                matched_lat=float(best["lat"]),
                matched_lon=float(best["lon"]),
                matched_dep=float(best["dep"]),
                matched_mag=float(best["mag"]),
                time_diff_sec=float(best["time_diff_sec"]),
                horizontal_distance_km=float(best["horizontal_distance_km"]),
                depth_diff_km=float(best["depth_diff_km"]),
                combined_score=float(best["combined_score"]),
                n_close_candidates=n_close,
                candidate_preview=json.dumps(
                    preview_df.applymap(to_jsonable).to_dict(orient="records"),
                    ensure_ascii=False,
                ),
                match_status=status,
            ))
        else:
            matches.append(MainshockMatch(
                label=row["index"], ref_datetime=row["datetime"], ref_lat=float(row["lat"]), ref_lon=float(row["lon"]), ref_dep=float(row["dep"]), ref_mag=float(row["mag"]),
                matched_index=None, matched_datetime=None, matched_lat=None, matched_lon=None, matched_dep=None, matched_mag=None,
                time_diff_sec=None, horizontal_distance_km=None, depth_diff_km=None, combined_score=None, n_close_candidates=0,
                candidate_preview="[]", match_status="unmatched",
            ))
    match_df = pd.DataFrame([m.__dict__ for m in matches])
    preview_df = pd.DataFrame(previews)
    return match_df, preview_df


def summarize_mecha_coverage(mecha_df: pd.DataFrame, match_df: pd.DataFrame) -> pd.DataFrame:
    if mecha_df.empty:
        return pd.DataFrame([
            {
                "mainshock": mr["label"],
                "mechanism_events_within_1day_50km": 0,
                "mechanism_events_within_7day_100km": 0,
                "available": False,
            }
            for _, mr in match_df.iterrows()
        ])
    mecha = mecha_df.copy()
    mecha["origin_time"] = parse_time_series(mecha["origin_time"])
    rows = []
    for _, mr in match_df.iterrows():
        if pd.isna(mr["matched_datetime"]):
            rows.append({"mainshock": mr["label"], "mechanism_events_within_1day_50km": 0, "mechanism_events_within_7day_100km": 0, "available": False})
            continue
        dt = mr["matched_datetime"]
        dts = (mecha["origin_time"] - dt).dt.total_seconds().abs()
        dist = haversine_km(mr["matched_lat"], mr["matched_lon"], mecha["lat_deg"].to_numpy(), mecha["lon_deg"].to_numpy())
        rows.append({
            "mainshock": mr["label"],
            "mechanism_events_within_1day_50km": int(((dts <= 86400) & (dist <= 50)).sum()),
            "mechanism_events_within_7day_100km": int(((dts <= 7 * 86400) & (dist <= 100)).sum()),
            "available": bool(len(mecha) > 0),
        })
    return pd.DataFrame(rows)


def summarize_station_coverage(sta_df: pd.DataFrame) -> pd.DataFrame:
    out = {
        "n_stations": int(len(sta_df)),
        "lat_min": float(sta_df["latitude"].min()) if "latitude" in sta_df.columns else np.nan,
        "lat_max": float(sta_df["latitude"].max()) if "latitude" in sta_df.columns else np.nan,
        "lon_min": float(sta_df["longitude"].min()) if "longitude" in sta_df.columns else np.nan,
        "lon_max": float(sta_df["longitude"].max()) if "longitude" in sta_df.columns else np.nan,
        "matched_true": int(sta_df["matched"].astype(str).str.lower().eq("true").sum()) if "matched" in sta_df.columns else None,
        "matched_false": int(sta_df["matched"].astype(str).str.lower().eq("false").sum()) if "matched" in sta_df.columns else None,
    }
    return pd.DataFrame([out])


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
    log(f"[0] Cleaned {removed} stale output artifacts in {OUTPUT_DIR}")


def main() -> None:
    clean_output_dir()
    log(f"[1] Reading inputs from {BASE_DIR}")

    cat = pd.read_csv(CATALOG_PATH)
    main_df = pd.read_csv(MAIN_PATH)
    mecha = pd.read_csv(MECHA_PATH)
    sta = pd.read_csv(STATION_PATH)

    cat["datetime"] = parse_time_series(cat["datetime"])
    main_df["datetime"] = parse_time_series(main_df["datetime"])
    mecha["origin_time"] = parse_time_series(mecha["origin_time"])
    if "matched" in sta.columns:
        sta["matched"] = sta["matched"].astype(str)

    log("[2] Verifying schema and basic field availability")
    verification = {
        "catalog": verify_catalog(cat, CATALOG_PATH),
        "main_earthquake": verify_main(main_df, MAIN_PATH),
        "mechanism": verify_mecha(mecha, MECHA_PATH),
        "stations": verify_station(sta, STATION_PATH),
    }

    log("[3] Rematching mainshocks to relocated catalog")
    match_df, candidate_preview_df = match_mainshocks(main_df, cat)
    mech_cov = summarize_mecha_coverage(mecha, match_df)
    station_cov = summarize_station_coverage(sta)

    # enrich with match deltas for direct comparison to the reference table
    match_df["time_diff_min"] = match_df["time_diff_sec"] / 60.0
    match_df["ref_time"] = match_df["ref_datetime"].astype(str)
    match_df["matched_time"] = match_df["matched_datetime"].astype(str)
    match_df["ref_location"] = match_df.apply(lambda r: f"{r['ref_lat']:.5f},{r['ref_lon']:.5f}", axis=1)
    match_df["matched_location"] = match_df.apply(lambda r: None if pd.isna(r["matched_lat"]) else f"{r['matched_lat']:.5f},{r['matched_lon']:.5f}", axis=1)
    required_post_cols = ["time_diff_min", "ref_time", "matched_time", "ref_location", "matched_location"]
    missing_post_cols = [c for c in required_post_cols if c not in match_df.columns]
    if missing_post_cols:
        raise RuntimeError(f"Match table missing expected downstream columns: {missing_post_cols}")

    # save outputs
    cat_audit_path = OUTPUT_DIR / "field_verification_catalog.json"
    main_audit_path = OUTPUT_DIR / "field_verification_main_earthquake.json"
    mecha_audit_path = OUTPUT_DIR / "field_verification_mechanism.json"
    station_audit_path = OUTPUT_DIR / "field_verification_stations.json"
    match_path = OUTPUT_DIR / "matched_mainshocks.csv"
    mech_cov_path = OUTPUT_DIR / "mechanism_coverage_summary.csv"
    station_cov_path = OUTPUT_DIR / "station_coverage_summary.csv"
    preview_path = OUTPUT_DIR / "mainshock_candidate_preview.json"
    verification_path = OUTPUT_DIR / "verification_summary.json"

    with open(cat_audit_path, "w", encoding="utf-8") as f:
        json.dump(verification["catalog"], f, indent=2, default=str)
    with open(main_audit_path, "w", encoding="utf-8") as f:
        json.dump(verification["main_earthquake"], f, indent=2, default=str)
    with open(mecha_audit_path, "w", encoding="utf-8") as f:
        json.dump(verification["mechanism"], f, indent=2, default=str)
    with open(station_audit_path, "w", encoding="utf-8") as f:
        json.dump(verification["stations"], f, indent=2, default=str)
    with open(preview_path, "w", encoding="utf-8") as f:
        json.dump(candidate_preview_df.applymap(to_jsonable).to_dict(orient="records"), f, indent=2, default=str)
    with open(verification_path, "w", encoding="utf-8") as f:
        json.dump({
            "inputs": verification,
            "n_mainshocks": int(len(main_df)),
            "n_catalog_events": int(len(cat)),
            "n_mechanism_events": int(len(mecha)),
            "n_stations": int(len(sta)),
            "match_status_counts": match_df["match_status"].value_counts(dropna=False).to_dict(),
        }, f, indent=2, default=str)

    match_df.to_csv(match_path, index=False)
    mech_cov.to_csv(mech_cov_path, index=False)
    station_cov.to_csv(station_cov_path, index=False)

    log(f"[4] Saved match table to {match_path}")
    log(f"[4] Saved verification outputs to {OUTPUT_DIR}")
    log("[5] Match summary:")
    log(match_df[["label", "matched_index", "time_diff_sec", "horizontal_distance_km", "depth_diff_km", "match_status"]].to_string(index=False))
    log("[5] Mechanism coverage summary:")
    log(mech_cov.to_string(index=False))
    log("[5] Station coverage summary:")
    log(station_cov.to_string(index=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
