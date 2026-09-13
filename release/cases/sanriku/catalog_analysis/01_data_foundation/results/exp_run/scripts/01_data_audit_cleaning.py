from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
import pandas as pd


DATA_DIR = Path(
    "<CASE_ROOT>/data"
)
OUTPUT_DIR = Path(
    "<CASE_ROOT>/run/01_data_foundation/exp_run/outputs/01_data_audit_cleaning"
)

REGIONAL_CATALOG = DATA_DIR / "catalog/Snet_catalog_relocate.csv"
MAINSHOCKS = DATA_DIR / "catalog/main_earthquake.csv"
MECHANISMS = DATA_DIR / "source_mechanism/Snet_mecha.csv"
STATIONS = DATA_DIR / "stations/station.sta"

EARTH_RADIUS_KM = 6371.0088
EXPECTED_REGION = {
    "lat_min": 33.0,
    "lat_max": 46.0,
    "lon_min": 138.0,
    "lon_max": 147.5,
    "depth_min": -5.0,
    "depth_max": 700.0,
    "mag_min": -1.0,
    "mag_max": 10.0,
}


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def detect_time_column(columns: Iterable[str]) -> Optional[str]:
    candidates = ["datetime", "origin_time", "time", "event_time", "origin"]
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand in lower_map:
            return lower_map[cand]
    return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df


def audit_dataframe(name: str, df: pd.DataFrame, time_col: Optional[str]) -> Dict[str, object]:
    audit: Dict[str, object] = {
        "file_name": name,
        "record_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "columns": ",".join(df.columns.astype(str).tolist()),
        "missing_values_total": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "usable_fields": ",".join(df.columns.astype(str).tolist()),
        "time_column": time_col or "",
    }
    if time_col and time_col in df.columns:
        parsed = pd.to_datetime(df[time_col], errors="coerce", utc=True)
        audit["time_parse_success"] = int(parsed.notna().sum())
        audit["time_parse_failure"] = int(parsed.isna().sum())
        if parsed.notna().any():
            audit["time_min"] = parsed.min().isoformat()
            audit["time_max"] = parsed.max().isoformat()
    else:
        audit["time_parse_success"] = 0
        audit["time_parse_failure"] = 0
        audit["time_min"] = ""
        audit["time_max"] = ""
    return audit


def infer_event_id_column(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        lc = col.lower()
        if lc in {"index", "event_id", "event_code", "id", "eid"}:
            return col
    return None


def build_clean_catalog(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    time_col = detect_time_column(df.columns)
    if time_col is None:
        raise ValueError("No recognizable time column found in regional catalog.")

    out = pd.DataFrame(index=df.index)
    out["source_file"] = "Snet_catalog_relocate.csv"
    out["raw_time"] = df[time_col].astype(str)
    out["origin_time"] = pd.to_datetime(df[time_col], errors="coerce", utc=True)
    out["latitude"] = pd.to_numeric(df.get("lat"), errors="coerce")
    out["longitude"] = pd.to_numeric(df.get("lon"), errors="coerce")
    out["depth_km"] = pd.to_numeric(df.get("dep"), errors="coerce")
    out["magnitude"] = pd.to_numeric(df.get("mag"), errors="coerce")

    event_id_col = infer_event_id_column(df)
    if event_id_col is not None:
        out["event_id"] = df[event_id_col].astype(str)
    else:
        out["event_id"] = [f"CAT_{i:06d}" for i in range(len(df))]

    out["has_origin_time"] = out["origin_time"].notna()
    out["has_location"] = out[["latitude", "longitude"]].notna().all(axis=1)
    out["has_depth"] = out["depth_km"].notna()
    out["has_magnitude"] = out["magnitude"].notna()

    out["flag_time_parse_failed"] = ~out["has_origin_time"]
    out["flag_missing_location"] = ~out["has_location"]
    out["flag_missing_depth"] = ~out["has_depth"]
    out["flag_missing_magnitude"] = ~out["has_magnitude"]

    out["flag_lat_out_of_bounds"] = ~out["latitude"].between(EXPECTED_REGION["lat_min"], EXPECTED_REGION["lat_max"], inclusive="both")
    out["flag_lon_out_of_bounds"] = ~out["longitude"].between(EXPECTED_REGION["lon_min"], EXPECTED_REGION["lon_max"], inclusive="both")
    out["flag_depth_out_of_bounds"] = ~out["depth_km"].between(EXPECTED_REGION["depth_min"], EXPECTED_REGION["depth_max"], inclusive="both")
    out["flag_mag_out_of_bounds"] = ~out["magnitude"].between(EXPECTED_REGION["mag_min"], EXPECTED_REGION["mag_max"], inclusive="both")

    out["flag_any_quality_issue"] = out[
        [
            "flag_time_parse_failed",
            "flag_missing_location",
            "flag_missing_depth",
            "flag_missing_magnitude",
            "flag_lat_out_of_bounds",
            "flag_lon_out_of_bounds",
            "flag_depth_out_of_bounds",
            "flag_mag_out_of_bounds",
        ]
    ].any(axis=1)
    out["quality_status"] = np.where(out["flag_any_quality_issue"], "needs_review", "clean")

    dup_sig = (
        out["origin_time"].dt.round("1s").astype("int64", errors="ignore").astype(str)
        + "|"
        + out["latitude"].round(4).astype(str)
        + "|"
        + out["longitude"].round(4).astype(str)
        + "|"
        + out["depth_km"].round(2).astype(str)
        + "|"
        + out["magnitude"].round(2).astype(str)
    )
    out["duplicate_signature"] = dup_sig
    out["flag_exact_duplicate_signature"] = out.duplicated("duplicate_signature", keep=False)
    return out


def haversine_km(lon1, lat1, lon2, lat2):
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def summarize_numeric(s: pd.Series) -> Dict[str, object]:
    s = pd.to_numeric(s, errors="coerce")
    return {
        "count": int(s.notna().sum()),
        "min": float(s.min()) if s.notna().any() else np.nan,
        "p01": float(s.quantile(0.01)) if s.notna().any() else np.nan,
        "p05": float(s.quantile(0.05)) if s.notna().any() else np.nan,
        "median": float(s.median()) if s.notna().any() else np.nan,
        "p95": float(s.quantile(0.95)) if s.notna().any() else np.nan,
        "p99": float(s.quantile(0.99)) if s.notna().any() else np.nan,
        "max": float(s.max()) if s.notna().any() else np.nan,
        "mean": float(s.mean()) if s.notna().any() else np.nan,
        "std": float(s.std(ddof=1)) if s.notna().sum() > 1 else np.nan,
    }


def parse_station_table(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    out = pd.DataFrame(index=df.index)
    out["station_code"] = df.get("station_code").astype(str)
    out["station_number"] = pd.to_numeric(df.get("station_number"), errors="coerce")
    out["latitude"] = pd.to_numeric(df.get("latitude"), errors="coerce")
    out["longitude"] = pd.to_numeric(df.get("longitude"), errors="coerce")
    out["elevation_m"] = pd.to_numeric(df.get("elevation_m"), errors="coerce")
    matched = df.get("matched")
    if matched is not None:
        out["matched"] = matched.astype(str).str.lower().isin(["true", "1", "yes", "y"])
    else:
        out["matched"] = False
    out["flag_any_quality_issue"] = out[["station_code", "station_number", "latitude", "longitude"]].isna().any(axis=1)
    return out


def parse_mechanisms(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    out = pd.DataFrame(index=df.index)
    out["event_code"] = df.get("event_code").astype(str)
    out["origin_time"] = pd.to_datetime(df.get("origin_time"), errors="coerce", utc=True)
    out["latitude"] = pd.to_numeric(df.get("lat_deg"), errors="coerce")
    out["longitude"] = pd.to_numeric(df.get("lon_deg"), errors="coerce")
    out["depth_km"] = pd.to_numeric(df.get("depth_km"), errors="coerce")
    out["mag_1"] = pd.to_numeric(df.get("mag_1"), errors="coerce")
    out["mag_2"] = pd.to_numeric(df.get("mag_2"), errors="coerce")
    mech_cols = ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip", "N_axis_azimuth", "N_axis_dip", "strike_plane1", "dip_plane1", "rake_plane1", "strike_plane2", "dip_plane2", "rake_plane2"]
    for c in mech_cols + ["focal_mech_score", "n_hypo_stations", "n_mech_stations"]:
        if c in df.columns:
            out[c] = pd.to_numeric(df.get(c), errors="coerce")
    out["has_geometry"] = out[[c for c in mech_cols if c in out.columns]].notna().any(axis=1)
    out["has_mechanism_core"] = out[["strike_plane1", "dip_plane1", "rake_plane1"]].notna().all(axis=1) if {"strike_plane1", "dip_plane1", "rake_plane1"}.issubset(out.columns) else False
    return out


def main() -> None:
    try:
        ensure_output_dir(OUTPUT_DIR)

        for stale_name in [
            "stage1_regional_catalog_clean.csv",
            "main_earthquake_clean.csv",
            "source_mechanism_clean.csv",
            "station_clean.csv",
            "file_level_audit_summary.csv",
            "quality_summary.csv",
            "regional_catalog_numeric_summary.csv",
            "main_earthquake_numeric_summary.csv",
            "field_mapping_summary.csv",
            "duplicate_signature_report.csv",
            "abnormal_value_report.csv",
            "station_summary.csv",
            "mechanism_summary.csv",
        ]:
            stale_path = OUTPUT_DIR / stale_name
            if stale_path.exists():
                stale_path.unlink()

        cat_raw = pd.read_csv(REGIONAL_CATALOG)
        main_raw = pd.read_csv(MAINSHOCKS)
        mecha_raw = pd.read_csv(MECHANISMS)
        sta_raw = pd.read_csv(STATIONS)

        cat_clean = build_clean_catalog(cat_raw)
        main_clean = build_clean_catalog(main_raw.rename(columns={"index": "event_id"}))
        mecha_clean = parse_mechanisms(mecha_raw)
        sta_clean = parse_station_table(sta_raw)

        required_cat_cols = {"origin_time", "latitude", "longitude", "depth_km", "magnitude", "event_id", "quality_status"}
        required_main_cols = {"origin_time", "latitude", "longitude", "depth_km", "magnitude", "event_id", "quality_status"}
        missing_cat = required_cat_cols.difference(cat_clean.columns)
        missing_main = required_main_cols.difference(main_clean.columns)
        if missing_cat:
            raise ValueError(f"Stage-1 catalog missing required columns: {sorted(missing_cat)}")
        if missing_main:
            raise ValueError(f"Main earthquake cleaned table missing required columns: {sorted(missing_main)}")

        cat_clean = cat_clean.sort_values("origin_time", na_position="last").reset_index(drop=True)
        main_clean = main_clean.sort_values("origin_time", na_position="last").reset_index(drop=True)
        mecha_clean = mecha_clean.sort_values("origin_time", na_position="last").reset_index(drop=True)
        sta_clean = sta_clean.sort_values(["station_code"]).reset_index(drop=True)

        audits = []
        audits.append(audit_dataframe("Snet_catalog_relocate.csv", cat_raw, detect_time_column(cat_raw.columns)))
        audits.append(audit_dataframe("main_earthquake.csv", main_raw, detect_time_column(main_raw.columns)))
        audits.append(audit_dataframe("Snet_mecha.csv", mecha_raw, detect_time_column(mecha_raw.columns)))
        audits.append(audit_dataframe("station.sta", sta_raw, detect_time_column(sta_raw.columns)))
        audit_df = pd.DataFrame(audits)

        quality_summary = pd.DataFrame(
            [
                {
                    "dataset": "regional_catalog",
                    "records": len(cat_clean),
                    "clean_records": int((~cat_clean["flag_any_quality_issue"]).sum()),
                    "issue_records": int(cat_clean["flag_any_quality_issue"].sum()),
                    "duplicate_signatures": int(cat_clean["flag_exact_duplicate_signature"].sum()),
                    "time_parse_failures": int(cat_clean["flag_time_parse_failed"].sum()),
                    "lat_out_of_bounds": int(cat_clean["flag_lat_out_of_bounds"].sum()),
                    "lon_out_of_bounds": int(cat_clean["flag_lon_out_of_bounds"].sum()),
                    "depth_out_of_bounds": int(cat_clean["flag_depth_out_of_bounds"].sum()),
                    "mag_out_of_bounds": int(cat_clean["flag_mag_out_of_bounds"].sum()),
                },
                {
                    "dataset": "main_earthquake",
                    "records": len(main_clean),
                    "clean_records": int((~main_clean["flag_any_quality_issue"]).sum()),
                    "issue_records": int(main_clean["flag_any_quality_issue"].sum()),
                    "duplicate_signatures": int(main_clean["flag_exact_duplicate_signature"].sum()),
                    "time_parse_failures": int(main_clean["flag_time_parse_failed"].sum()),
                    "lat_out_of_bounds": int(main_clean["flag_lat_out_of_bounds"].sum()),
                    "lon_out_of_bounds": int(main_clean["flag_lon_out_of_bounds"].sum()),
                    "depth_out_of_bounds": int(main_clean["flag_depth_out_of_bounds"].sum()),
                    "mag_out_of_bounds": int(main_clean["flag_mag_out_of_bounds"].sum()),
                },
            ]
        )

        cat_numeric_summary = pd.DataFrame(
            {
                "latitude": summarize_numeric(cat_clean["latitude"]),
                "longitude": summarize_numeric(cat_clean["longitude"]),
                "depth_km": summarize_numeric(cat_clean["depth_km"]),
                "magnitude": summarize_numeric(cat_clean["magnitude"]),
            }
        )
        main_numeric_summary = pd.DataFrame(
            {
                "latitude": summarize_numeric(main_clean["latitude"]),
                "longitude": summarize_numeric(main_clean["longitude"]),
                "depth_km": summarize_numeric(main_clean["depth_km"]),
                "magnitude": summarize_numeric(main_clean["magnitude"]),
            }
        )

        cat_clean.to_csv(OUTPUT_DIR / "stage1_regional_catalog_clean.csv", index=False)
        main_clean.to_csv(OUTPUT_DIR / "main_earthquake_clean.csv", index=False)
        mecha_clean.to_csv(OUTPUT_DIR / "source_mechanism_clean.csv", index=False)
        sta_clean.to_csv(OUTPUT_DIR / "station_clean.csv", index=False)

        audit_df.to_csv(OUTPUT_DIR / "file_level_audit_summary.csv", index=False)
        quality_summary.to_csv(OUTPUT_DIR / "quality_summary.csv", index=False)
        cat_numeric_summary.to_csv(OUTPUT_DIR / "regional_catalog_numeric_summary.csv")
        main_numeric_summary.to_csv(OUTPUT_DIR / "main_earthquake_numeric_summary.csv")

        field_summary = pd.DataFrame(
            [
                {"file": "Snet_catalog_relocate.csv", "usable_fields": "datetime,lat,lon,dep,mag", "time_column": "datetime"},
                {"file": "main_earthquake.csv", "usable_fields": "index,datetime,lat,lon,dep,mag", "time_column": "datetime"},
                {"file": "Snet_mecha.csv", "usable_fields": ",".join(mecha_raw.columns.astype(str).tolist()), "time_column": "origin_time"},
                {"file": "station.sta", "usable_fields": ",".join(sta_raw.columns.astype(str).tolist()), "time_column": ""},
            ]
        )
        field_summary.to_csv(OUTPUT_DIR / "field_mapping_summary.csv", index=False)

        duplicate_report = cat_clean.loc[cat_clean["flag_exact_duplicate_signature"], ["event_id", "origin_time", "latitude", "longitude", "depth_km", "magnitude", "duplicate_signature"]]
        duplicate_report.to_csv(OUTPUT_DIR / "duplicate_signature_report.csv", index=False)

        abnormal_report = cat_clean.loc[
            cat_clean[
                ["flag_lat_out_of_bounds", "flag_lon_out_of_bounds", "flag_depth_out_of_bounds", "flag_mag_out_of_bounds", "flag_time_parse_failed"]
            ].any(axis=1),
            ["event_id", "raw_time", "origin_time", "latitude", "longitude", "depth_km", "magnitude", "quality_status", "flag_lat_out_of_bounds", "flag_lon_out_of_bounds", "flag_depth_out_of_bounds", "flag_mag_out_of_bounds", "flag_time_parse_failed"],
        ]
        abnormal_report.to_csv(OUTPUT_DIR / "abnormal_value_report.csv", index=False)

        station_summary = pd.DataFrame(
            [{
                "station_count": len(sta_clean),
                "matched_count": int(sta_clean["matched"].sum()),
                "latitude_min": float(sta_clean["latitude"].min()),
                "latitude_max": float(sta_clean["latitude"].max()),
                "longitude_min": float(sta_clean["longitude"].min()),
                "longitude_max": float(sta_clean["longitude"].max()),
                "elevation_min_m": float(sta_clean["elevation_m"].min()),
                "elevation_max_m": float(sta_clean["elevation_m"].max()),
            }]
        )
        station_summary.to_csv(OUTPUT_DIR / "station_summary.csv", index=False)

        mechanism_summary = pd.DataFrame(
            [{
                "record_count": len(mecha_clean),
                "origin_time_parse_success": int(mecha_clean["origin_time"].notna().sum()),
                "latitude_nonmissing": int(mecha_clean["latitude"].notna().sum()),
                "longitude_nonmissing": int(mecha_clean["longitude"].notna().sum()),
                "depth_nonmissing": int(mecha_clean["depth_km"].notna().sum()),
                "core_mechanism_available": int(mecha_clean["has_mechanism_core"].sum()) if "has_mechanism_core" in mecha_clean.columns else 0,
                "geometry_available": int(mecha_clean["has_geometry"].sum()) if "has_geometry" in mecha_clean.columns else 0,
            }]
        )
        mechanism_summary.to_csv(OUTPUT_DIR / "mechanism_summary.csv", index=False)

        print("[01_data_audit_cleaning] Completed successfully.", flush=True)
        print(f"[01_data_audit_cleaning] Output directory: {OUTPUT_DIR}", flush=True)
        print(f"[01_data_audit_cleaning] Clean regional catalog rows: {len(cat_clean)}", flush=True)
        print(f"[01_data_audit_cleaning] Clean main earthquakes rows: {len(main_clean)}", flush=True)
        print(f"[01_data_audit_cleaning] Mechanism rows: {len(mecha_clean)}", flush=True)
        print(f"[01_data_audit_cleaning] Station rows: {len(sta_clean)}", flush=True)

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
