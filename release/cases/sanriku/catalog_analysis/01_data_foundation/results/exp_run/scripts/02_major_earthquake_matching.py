from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


DATA_DIR = Path(
    "<CASE_ROOT>/data"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/02_major_earthquake_matching"
)
STAGE1_OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning"
)

REGIONAL_CATALOG = DATA_DIR / "catalog/Snet_catalog_relocate.csv"
MAINSHOCKS = DATA_DIR / "catalog/main_earthquake.csv"

EARTH_RADIUS_KM = 6371.0088
PRIMARY_TIME_WINDOW_HOURS = 6.0
SECONDARY_TIME_WINDOW_HOURS = 48.0
TIE_TIME_TOL_SEC = 60.0
TIE_DIST_TOL_KM = 10.0
TIE_DEPTH_TOL_KM = 20.0
TIE_MAG_TOL = 0.3


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def detect_time_column(columns) -> Optional[str]:
    candidates = ["datetime", "origin_time", "time", "event_time", "origin"]
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


def haversine_km(lon1, lat1, lon2, lat2):
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def load_stage1_catalog() -> pd.DataFrame:
    stage1_path = STAGE1_OUTPUT_DIR / "stage1_regional_catalog_clean.csv"
    if stage1_path.exists():
        df = pd.read_csv(stage1_path)
        df = normalize_columns(df)
        df["origin_time"] = pd.to_datetime(df["origin_time"], errors="coerce", utc=True)
        return df

    raw = pd.read_csv(REGIONAL_CATALOG)
    raw = normalize_columns(raw)
    time_col = detect_time_column(raw.columns)
    if time_col is None:
        raise ValueError("No recognizable time column in regional catalog")
    out = pd.DataFrame(index=raw.index)
    out["source_file"] = "Snet_catalog_relocate.csv"
    out["raw_time"] = raw[time_col].astype(str)
    out["origin_time"] = pd.to_datetime(raw[time_col], errors="coerce", utc=True)
    out["latitude"] = pd.to_numeric(raw.get("lat"), errors="coerce")
    out["longitude"] = pd.to_numeric(raw.get("lon"), errors="coerce")
    out["depth_km"] = pd.to_numeric(raw.get("dep"), errors="coerce")
    out["magnitude"] = pd.to_numeric(raw.get("mag"), errors="coerce")
    out["event_id"] = [f"CAT_{i:06d}" for i in range(len(out))]
    return out


def load_mainshocks() -> pd.DataFrame:
    df = pd.read_csv(MAINSHOCKS)
    df = normalize_columns(df)
    time_col = detect_time_column(df.columns)
    if time_col is None:
        raise ValueError("No recognizable time column in main_earthquake.csv")
    out = pd.DataFrame(index=df.index)
    out["reference_id"] = df.get("index", pd.Series([f"M{i+1}" for i in range(len(df))]))
    out["raw_time"] = df[time_col].astype(str)
    out["origin_time"] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
    out["latitude"] = pd.to_numeric(df.get("lat"), errors="coerce")
    out["longitude"] = pd.to_numeric(df.get("lon"), errors="coerce")
    out["depth_km"] = pd.to_numeric(df.get("dep"), errors="coerce")
    out["magnitude"] = pd.to_numeric(df.get("mag"), errors="coerce")
    return out


def candidate_score(dt_sec: float, dist_km: float, depth_diff: float, mag_diff: float) -> float:
    return (
        abs(dt_sec) / 60.0
        + dist_km / 5.0
        + abs(depth_diff) / 10.0
        + abs(mag_diff) * 2.0
    )


def confidence_label(n_candidates: int, best: pd.Series, second: Optional[pd.Series], candidate_window_hours: float) -> str:
    if n_candidates == 0:
        return "unmatched"
    if second is None:
        return "high"
    score_gap = second["composite_score"] - best["composite_score"]
    time_gap = abs(second["time_diff_sec"]) - abs(best["time_diff_sec"])
    dist_gap = second["distance_km"] - best["distance_km"]
    if (
        abs(best["time_diff_sec"]) <= 300
        and best["distance_km"] <= 15
        and abs(best["depth_diff_km"]) <= 20
        and abs(best["mag_diff"]) <= 0.4
        and score_gap > 5
        and time_gap > TIE_TIME_TOL_SEC
        and dist_gap > TIE_DIST_TOL_KM
    ):
        return "high"
    if (
        abs(best["time_diff_sec"]) <= 1800
        and best["distance_km"] <= 40
        and abs(best["depth_diff_km"]) <= 40
        and abs(best["mag_diff"]) <= 0.8
        and score_gap > 1
    ):
        return "moderate"
    if candidate_window_hours <= PRIMARY_TIME_WINDOW_HOURS and n_candidates < 5:
        return "low"
    return "ambiguous"


def match_one(main_row: pd.Series, catalog: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    center = main_row["origin_time"]
    if pd.isna(center):
        result = main_row.to_dict()
        result.update({
            "matched_event_id": "",
            "matched_time": pd.NaT,
            "time_diff_sec": np.nan,
            "distance_km": np.nan,
            "depth_diff_km": np.nan,
            "mag_diff": np.nan,
            "candidate_count": 0,
            "search_window_hours": np.nan,
            "confidence": "unmatched",
            "match_note": "reference time parse failed",
        })
        return pd.Series(result), pd.DataFrame()

    search_hours = PRIMARY_TIME_WINDOW_HOURS
    cand = catalog[(catalog["origin_time"] >= center - pd.Timedelta(hours=search_hours)) & (catalog["origin_time"] <= center + pd.Timedelta(hours=search_hours))].copy()
    fallback_used = False
    if cand.empty:
        search_hours = SECONDARY_TIME_WINDOW_HOURS
        cand = catalog[(catalog["origin_time"] >= center - pd.Timedelta(hours=search_hours)) & (catalog["origin_time"] <= center + pd.Timedelta(hours=search_hours))].copy()
        fallback_used = True

    if cand.empty:
        result = main_row.to_dict()
        result.update({
            "matched_event_id": "",
            "matched_time": pd.NaT,
            "time_diff_sec": np.nan,
            "distance_km": np.nan,
            "depth_diff_km": np.nan,
            "mag_diff": np.nan,
            "candidate_count": 0,
            "search_window_hours": search_hours,
            "confidence": "unmatched",
            "match_note": "no catalog candidate in search window",
        })
        return pd.Series(result), pd.DataFrame()

    cand["time_diff_sec"] = (cand["origin_time"] - center).dt.total_seconds()
    cand["distance_km"] = haversine_km(main_row["longitude"], main_row["latitude"], cand["longitude"].to_numpy(), cand["latitude"].to_numpy())
    cand["depth_diff_km"] = cand["depth_km"] - main_row["depth_km"]
    cand["mag_diff"] = cand["magnitude"] - main_row["magnitude"]
    cand["composite_score"] = [candidate_score(a, b, c, d) for a, b, c, d in zip(cand["time_diff_sec"], cand["distance_km"], cand["depth_diff_km"], cand["mag_diff"])]
    cand = cand.sort_values(["composite_score", "time_diff_sec", "distance_km", "depth_diff_km"], ascending=[True, True, True, True]).reset_index(drop=True)

    best = cand.iloc[0]
    second = cand.iloc[1] if len(cand) > 1 else None
    confidence = confidence_label(len(cand), best, second, search_hours)
    if fallback_used and confidence != "unmatched":
        confidence = f"fallback_{confidence}"

    tie_flag = False
    if second is not None:
        tie_flag = (
            abs(second["time_diff_sec"] - best["time_diff_sec"]) <= TIE_TIME_TOL_SEC
            and abs(second["distance_km"] - best["distance_km"]) <= TIE_DIST_TOL_KM
            and abs(second["depth_diff_km"] - best["depth_diff_km"]) <= TIE_DEPTH_TOL_KM
            and abs(second["mag_diff"] - best["mag_diff"]) <= TIE_MAG_TOL
        )
        if tie_flag and confidence == "high":
            confidence = "ambiguous"

    result = main_row.to_dict()
    result.update({
        "matched_event_id": best["event_id"],
        "matched_time": best["origin_time"],
        "time_diff_sec": float(best["time_diff_sec"]),
        "distance_km": float(best["distance_km"]),
        "depth_diff_km": float(best["depth_diff_km"]),
        "mag_diff": float(best["mag_diff"]),
        "candidate_count": int(len(cand)),
        "search_window_hours": float(search_hours),
        "confidence": confidence,
        "match_note": "fallback window used" if fallback_used else "primary window used",
        "tie_flag": tie_flag,
    })
    return pd.Series(result), cand.head(10)


def build_summary(matches: pd.DataFrame) -> pd.DataFrame:
    n = len(matches)
    conf_counts = matches["confidence"].fillna("unknown").value_counts().sort_index()
    summary = pd.DataFrame([
        {"metric": "major_event_count", "value": n},
        {"metric": "matched_count", "value": int(matches["matched_event_id"].astype(str).str.len().gt(0).sum())},
        {"metric": "unmatched_count", "value": int((matches["matched_event_id"].astype(str).str.len() == 0).sum())},
        {"metric": "median_abs_time_diff_sec", "value": float(matches["time_diff_sec"].abs().median())},
        {"metric": "median_distance_km", "value": float(matches["distance_km"].median())},
        {"metric": "median_depth_diff_km", "value": float(matches["depth_diff_km"].abs().median())},
        {"metric": "median_mag_diff", "value": float(matches["mag_diff"].abs().median())},
    ])
    for conf, count in conf_counts.items():
        summary = pd.concat([summary, pd.DataFrame([{"metric": f"confidence_{conf}", "value": int(count)}])], ignore_index=True)
    return summary


def main() -> None:
    try:
        ensure_output_dir(OUTPUT_DIR)
        for stale in ["major_earthquake_matches.csv", "major_earthquake_candidates.csv", "major_earthquake_match_summary.csv"]:
            p = OUTPUT_DIR / stale
            if p.exists():
                p.unlink()

        catalog = load_stage1_catalog()
        mainshocks = load_mainshocks()
        catalog = catalog.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).reset_index(drop=True)
        mainshocks = mainshocks.reset_index(drop=True)

        all_matches: List[pd.Series] = []
        cand_rows: List[pd.DataFrame] = []
        for _, row in mainshocks.iterrows():
            matched_row, candidates = match_one(row, catalog)
            all_matches.append(matched_row)
            if not candidates.empty:
                candidates = candidates.copy()
                candidates.insert(0, "reference_id", row["reference_id"])
                cand_rows.append(candidates)

        match_df = pd.DataFrame(all_matches)
        candidate_df = pd.concat(cand_rows, ignore_index=True) if cand_rows else pd.DataFrame()
        summary_df = build_summary(match_df)

        required_match_cols = {
            "reference_id",
            "origin_time",
            "latitude",
            "longitude",
            "depth_km",
            "magnitude",
            "matched_event_id",
            "matched_time",
            "time_diff_sec",
            "distance_km",
            "depth_diff_km",
            "mag_diff",
            "candidate_count",
            "search_window_hours",
            "confidence",
            "match_note",
            "tie_flag",
        }
        missing_match_cols = required_match_cols.difference(match_df.columns)
        if missing_match_cols:
            raise ValueError(f"Match table missing required columns: {sorted(missing_match_cols)}")
        if not candidate_df.empty:
            required_candidate_cols = {
                "reference_id",
                "event_id",
                "origin_time",
                "latitude",
                "longitude",
                "depth_km",
                "magnitude",
                "time_diff_sec",
                "distance_km",
                "depth_diff_km",
                "mag_diff",
                "composite_score",
            }
            missing_candidate_cols = required_candidate_cols.difference(candidate_df.columns)
            if missing_candidate_cols:
                raise ValueError(f"Candidate table missing required columns: {sorted(missing_candidate_cols)}")

        match_df.to_csv(OUTPUT_DIR / "major_earthquake_matches.csv", index=False)
        if not candidate_df.empty:
            candidate_df.to_csv(OUTPUT_DIR / "major_earthquake_candidates.csv", index=False)
        else:
            pd.DataFrame(columns=["reference_id"]).to_csv(OUTPUT_DIR / "major_earthquake_candidates.csv", index=False)
        summary_df.to_csv(OUTPUT_DIR / "major_earthquake_match_summary.csv", index=False)

        print("[02_major_earthquake_matching] Completed successfully.", flush=True)
        print(f"[02_major_earthquake_matching] Output directory: {OUTPUT_DIR}", flush=True)
        print(f"[02_major_earthquake_matching] Major events: {len(mainshocks)}", flush=True)
        print(f"[02_major_earthquake_matching] Matched events: {match_df['matched_event_id'].astype(str).str.len().gt(0).sum()}", flush=True)
        print(f"[02_major_earthquake_matching] Candidate rows saved: {len(candidate_df)}", flush=True)

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
