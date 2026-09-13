from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


SCRIPT_PATH = Path(__file__).resolve()
OUTPUT_DIR = Path("<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/02_mechanism_coverage_audit")
DATA_DIR = Path("<CASE_ROOT>/data")
PRIMARY_OUTPUT_DIR = Path("<CASE_ROOT>/run/03_1C_mechanism_screening/exp_run/outputs/01_catalog_screening_analysis")

CATALOG_PATH = DATA_DIR / "catalog" / "Snet_catalog_relocate_250601_260501.csv"
MAIN_PATH = DATA_DIR / "catalog" / "main_earthquake.csv"
MECHA_PATH = DATA_DIR / "source_mechanism" / "Snet_mecha.csv"
VALIDATED_CATALOG_PATH = PRIMARY_OUTPUT_DIR / "validated_catalog.csv"
PRIMARY_JOIN_AUDIT_PATH = PRIMARY_OUTPUT_DIR / "mechanism_join_audit.csv"
PHASE_BOUNDARIES_PATH = PRIMARY_OUTPUT_DIR / "phase_boundaries.csv"

EARTH_RADIUS_KM = 6371.0
TIME_TOLERANCES_SEC = [1.0, 3.0, 5.0, 10.0]
HORIZONTAL_TOLERANCES_KM = [0.5, 1.0, 2.0, 5.0]
DEPTH_TOLERANCES_KM = [1.0, 2.0, 5.0, 10.0]
REPRESENTATIVE_MAG_THRESHOLDS = [3.0, 3.5, 4.0, 4.5, 5.0]
SPATIAL_CLASSES = [
    ("combined_local", "within_60km_either_m1_m3"),
    ("M1_extended", "within_60km_m1"),
    ("M3_extended", "within_60km_m3"),
    ("M1_core", "within_30km_m1"),
    ("M3_core", "within_30km_m3"),
    ("along_axis_20km", "along_axis_20km"),
    ("along_axis_30km", "along_axis_30km"),
    ("off_axis_20km", "off_axis_20km"),
    ("off_axis_30km", "off_axis_30km"),
    ("overlap_60km", "within_both_60km"),
]
PHASE_ORDER = [
    "baseline_to_M1_minus14d",
    "M1_related_M1minus14d_to_M1plus21d",
    "middle_M1plus21d_to_M3minus35d",
    "preM3_M3minus35d_to_M3",
    "post_M3_context",
    "outside_key_window",
]


@dataclass
class MainEvent:
    label: str
    time: pd.Timestamp
    lat: float
    lon: float
    depth_km: float
    mag: float


@dataclass
class MatchConfig:
    time_tol_sec: float
    horizontal_tol_km: float
    depth_tol_km: float


def log(message: str) -> None:
    print(message, flush=True)


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    removed = 0
    for pattern in ["*.csv", "*.png", "*.jpg", "*.jpeg", "*.txt"]:
        for path in OUTPUT_DIR.glob(pattern):
            if path.is_file():
                path.unlink()
                removed += 1
    log(f"Prepared output directory {OUTPUT_DIR}; removed {removed} stale quick-regenerate files")


def require_columns(df: pd.DataFrame, required: List[str], context: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {context}: {missing}")


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(np.asarray(lat1, dtype=float))
    lon1 = np.radians(np.asarray(lon1, dtype=float))
    lat2 = np.radians(np.asarray(lat2, dtype=float))
    lon2 = np.radians(np.asarray(lon2, dtype=float))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def load_mainshocks() -> Dict[str, MainEvent]:
    df = pd.read_csv(MAIN_PATH)
    df = df.rename(columns={"index": "label", "dep": "depth_km"})
    require_columns(df, ["label", "datetime", "lat", "lon", "depth_km", "mag"], "mainshock table")
    df["time"] = pd.to_datetime(df["datetime"], utc=True)
    out: Dict[str, MainEvent] = {}
    for _, row in df.iterrows():
        out[row["label"]] = MainEvent(
            label=str(row["label"]),
            time=row["time"],
            lat=float(row["lat"]),
            lon=float(row["lon"]),
            depth_km=float(row["depth_km"]),
            mag=float(row["mag"]),
        )
    return out


def load_catalog_with_fallback() -> pd.DataFrame:
    if not VALIDATED_CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Required previous-task output not found: {VALIDATED_CATALOG_PATH}. "
            "This standalone audit depends on the validated catalog from task 01 and must not rebuild partial replacements from current-task fallback logic."
        )

    log(f"Loading validated catalog from primary analysis: {VALIDATED_CATALOG_PATH}")
    df = pd.read_csv(VALIDATED_CATALOG_PATH)
    require_columns(
        df,
        [
            "event_id",
            "datetime",
            "time",
            "lat",
            "lon",
            "depth_km",
            "mag",
            "phase_primary",
            "within_60km_either_m1_m3",
            "within_30km_m1",
            "within_60km_m1",
            "within_30km_m3",
            "within_60km_m3",
            "within_both_60km",
            "along_axis_20km",
            "along_axis_30km",
            "off_axis_20km",
            "off_axis_30km",
            "m2_related_flag",
            "dist_m1_km",
            "dist_m3_km",
        ],
        "validated catalog",
    )
    df["time"] = pd.to_datetime(df["time"], utc=True, format="mixed")
    return df.sort_values("time").reset_index(drop=True)


def load_mechanisms() -> pd.DataFrame:
    log(f"Loading mechanism metadata: {MECHA_PATH}")
    df = pd.read_csv(MECHA_PATH)
    require_columns(df, ["event_code", "origin_time", "lat_deg", "lon_deg", "depth_km", "mag_1"], "mechanism table")
    df["origin_time"] = pd.to_datetime(df["origin_time"], utc=True, errors="coerce")
    df = df.dropna(subset=["origin_time", "lat_deg", "lon_deg", "depth_km", "mag_1"]).copy()
    df["mecha_id"] = np.arange(1, len(df) + 1, dtype=int)
    df["has_focal_planes"] = df[["strike_plane1", "dip_plane1", "rake_plane1"]].notna().all(axis=1) if all(c in df.columns for c in ["strike_plane1", "dip_plane1", "rake_plane1"]) else False
    df["has_axes"] = df[["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip"]].notna().all(axis=1) if all(c in df.columns for c in ["P_axis_azimuth", "P_axis_dip", "T_axis_azimuth", "T_axis_dip"]) else False
    df["has_complete_mechanism"] = df["has_focal_planes"] & df["has_axes"]
    return df.sort_values("origin_time").reset_index(drop=True)


def build_candidate_pairs(catalog: pd.DataFrame, mecha: pd.DataFrame, config: MatchConfig) -> pd.DataFrame:
    records: List[Dict[str, object]] = []
    catalog_times = catalog["time"]
    for idx, row in mecha.iterrows():
        if idx % 25 == 0:
            log(f"Building candidate pairs: mechanism row {idx + 1}/{len(mecha)}")
        t0 = row["origin_time"]
        tmin = t0 - pd.Timedelta(seconds=config.time_tol_sec)
        tmax = t0 + pd.Timedelta(seconds=config.time_tol_sec)
        subset = catalog[(catalog_times >= tmin) & (catalog_times <= tmax)]
        if subset.empty:
            continue
        horiz = haversine_km(subset["lat"].to_numpy(), subset["lon"].to_numpy(), row["lat_deg"], row["lon_deg"])
        depth_diff = np.abs(subset["depth_km"].to_numpy(dtype=float) - float(row["depth_km"]))
        dt_sec = np.abs((subset["time"] - t0).dt.total_seconds().to_numpy(dtype=float))
        ok = (horiz <= config.horizontal_tol_km) & (depth_diff <= config.depth_tol_km)
        if not np.any(ok):
            continue
        subset_ok = subset.loc[ok].copy()
        horiz_ok = horiz[ok]
        depth_ok = depth_diff[ok]
        dt_ok = dt_sec[ok]
        for pos, (_, cat_row) in enumerate(subset_ok.iterrows()):
            score = dt_ok[pos] + 2.0 * horiz_ok[pos] + 0.25 * depth_ok[pos] + abs(float(cat_row["mag"]) - float(row["mag_1"]))
            records.append(
                {
                    "mecha_id": int(row["mecha_id"]),
                    "event_code": row["event_code"],
                    "catalog_event_id": int(cat_row["event_id"]),
                    "time_diff_sec": float(dt_ok[pos]),
                    "horizontal_diff_km": float(horiz_ok[pos]),
                    "depth_diff_km": float(depth_ok[pos]),
                    "mag_diff": float(abs(float(cat_row["mag"]) - float(row["mag_1"]))),
                    "match_score": float(score),
                }
            )
    return pd.DataFrame.from_records(records)


def select_best_unique_matches(candidates: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return candidates.copy()
    remaining = candidates.sort_values([
        "match_score", "time_diff_sec", "horizontal_diff_km", "depth_diff_km", "mag_diff", "mecha_id", "catalog_event_id"
    ]).copy()
    chosen: List[pd.Series] = []
    used_mecha = set()
    used_catalog = set()
    for _, row in remaining.iterrows():
        mecha_id = int(row["mecha_id"])
        cat_id = int(row["catalog_event_id"])
        if mecha_id in used_mecha or cat_id in used_catalog:
            continue
        chosen.append(row)
        used_mecha.add(mecha_id)
        used_catalog.add(cat_id)
    if not chosen:
        return remaining.iloc[0:0].copy()
    return pd.DataFrame(chosen).reset_index(drop=True)


def run_tolerance_grid(catalog: pd.DataFrame, mecha: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, MatchConfig]:
    grid_rows: List[Dict[str, object]] = []
    best_choice: Optional[Tuple[int, int, int, pd.DataFrame, MatchConfig]] = None
    best_score: Optional[Tuple[float, float, float, float]] = None
    for tsec in TIME_TOLERANCES_SEC:
        for hkm in HORIZONTAL_TOLERANCES_KM:
            for dkm in DEPTH_TOLERANCES_KM:
                config = MatchConfig(time_tol_sec=tsec, horizontal_tol_km=hkm, depth_tol_km=dkm)
                candidates = build_candidate_pairs(catalog, mecha, config)
                matches = select_best_unique_matches(candidates)
                matched_frac = 0.0 if len(mecha) == 0 else len(matches) / len(mecha)
                ambiguous_mecha = 0
                ambiguous_catalog = 0
                if not candidates.empty:
                    mecha_counts = candidates.groupby("mecha_id").size()
                    catalog_counts = candidates.groupby("catalog_event_id").size()
                    ambiguous_mecha = int((mecha_counts > 1).sum())
                    ambiguous_catalog = int((catalog_counts > 1).sum())
                row = {
                    "time_tol_sec": tsec,
                    "horizontal_tol_km": hkm,
                    "depth_tol_km": dkm,
                    "candidate_pairs": int(len(candidates)),
                    "matched_pairs": int(len(matches)),
                    "matched_fraction": float(matched_frac),
                    "ambiguous_mecha_rows": ambiguous_mecha,
                    "ambiguous_catalog_events": ambiguous_catalog,
                    "median_time_diff_sec": float(matches["time_diff_sec"].median()) if not matches.empty else np.nan,
                    "median_horizontal_diff_km": float(matches["horizontal_diff_km"].median()) if not matches.empty else np.nan,
                    "median_depth_diff_km": float(matches["depth_diff_km"].median()) if not matches.empty else np.nan,
                }
                grid_rows.append(row)
                ranking = (
                    matched_frac,
                    -ambiguous_mecha,
                    -ambiguous_catalog,
                    -(tsec + hkm + dkm),
                )
                if best_score is None or ranking > best_score:
                    best_score = ranking
                    best_choice = (len(candidates), len(matches), ambiguous_mecha + ambiguous_catalog, matches.copy(), config)
    if best_choice is None:
        raise RuntimeError("No tolerance-grid evaluation was produced")
    tolerance_df = pd.DataFrame(grid_rows).sort_values(
        ["matched_fraction", "matched_pairs", "candidate_pairs", "time_tol_sec", "horizontal_tol_km", "depth_tol_km"],
        ascending=[False, False, False, True, True, True],
    ).reset_index(drop=True)
    matches = best_choice[3]
    config = best_choice[4]
    return tolerance_df, matches, config


def merge_match_context(catalog: pd.DataFrame, mecha: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    cat_cols = [
        "event_id", "time", "datetime", "lat", "lon", "depth_km", "mag", "phase_primary", "m2_related_flag",
        "dist_m1_km", "dist_m3_km",
    ] + [col for _, col in SPATIAL_CLASSES]
    require_columns(catalog, cat_cols, "catalog before context merge")
    cat_use = catalog[cat_cols].copy().rename(columns={
        "event_id": "catalog_event_id",
        "time": "catalog_time",
        "lat": "catalog_lat",
        "lon": "catalog_lon",
        "depth_km": "catalog_depth_km",
        "mag": "catalog_mag",
    })
    mecha_cols = [
        "mecha_id", "event_code", "origin_time", "lat_deg", "lon_deg", "depth_km", "mag_1", "mag_2",
        "focal_mech_score", "focal_mech_projection", "m_method", "m_source", "n_mech_stations",
        "has_focal_planes", "has_axes", "has_complete_mechanism",
        "P_axis_azimuth", "T_axis_azimuth", "strike_plane1", "dip_plane1", "rake_plane1",
        "strike_plane2", "dip_plane2", "rake_plane2",
    ]
    require_columns(mecha, ["mecha_id", "event_code", "origin_time", "lat_deg", "lon_deg", "depth_km", "mag_1"], "mechanism table before context merge")
    mecha_use = mecha[[col for col in mecha_cols if col in mecha.columns]].copy().rename(columns={
        "origin_time": "mecha_time",
        "lat_deg": "mecha_lat",
        "lon_deg": "mecha_lon",
        "depth_km": "mecha_depth_km",
        "mag_1": "mecha_mag_1",
        "mag_2": "mecha_mag_2",
    })
    if matches.empty:
        empty = matches.copy()
        out = empty.merge(mecha_use.iloc[0:0], on="mecha_id", how="left").merge(cat_use.iloc[0:0], on="catalog_event_id", how="left")
        out["mag_bin"] = pd.Categorical([], categories=["<3.0", "3.0-3.4", "3.5-3.9", "4.0-4.4", "4.5-4.9", ">=5.0"], ordered=True)
        out["mechanism_detail_class"] = pd.Series(dtype="object")
        out["is_local_zone_match"] = pd.Series(dtype="bool")
        return out
    out = matches.merge(mecha_use, on="mecha_id", how="left").merge(cat_use, on="catalog_event_id", how="left")
    require_columns(out, ["catalog_mag", "has_complete_mechanism", "has_focal_planes", "has_axes", "within_60km_either_m1_m3", "dist_m1_km", "dist_m3_km"], "merged mechanism-context table")
    out["mag_bin"] = pd.cut(
        out["catalog_mag"],
        bins=[-np.inf, 2.99, 3.49, 3.99, 4.49, 4.99, np.inf],
        labels=["<3.0", "3.0-3.4", "3.5-3.9", "4.0-4.4", "4.5-4.9", ">=5.0"],
        ordered=True,
    )
    out["mechanism_detail_class"] = np.select(
        [out["has_complete_mechanism"], out["has_focal_planes"] | out["has_axes"]],
        ["complete_mechanism", "partial_mechanism"],
        default="metadata_only",
    )
    out["is_local_zone_match"] = out["within_60km_either_m1_m3"].fillna(False)
    return out


def summarize_matching(catalog: pd.DataFrame, mecha: pd.DataFrame, matches: pd.DataFrame, config: MatchConfig, tolerance_df: pd.DataFrame) -> pd.DataFrame:
    matched_ids = set(matches["catalog_event_id"].astype(int).tolist()) if not matches.empty else set()
    metrics: List[Dict[str, object]] = [
        {"metric": "catalog_total_events", "value": float(len(catalog))},
        {"metric": "catalog_local_zone_events", "value": float(catalog["within_60km_either_m1_m3"].sum())},
        {"metric": "mecha_total_rows", "value": float(len(mecha))},
        {"metric": "matched_mecha_rows", "value": float(len(matches))},
        {"metric": "matched_fraction_of_mecha_rows", "value": float(0.0 if len(mecha) == 0 else len(matches) / len(mecha))},
        {"metric": "unique_catalog_events_with_mecha", "value": float(len(matched_ids))},
        {"metric": "catalog_fraction_with_mecha_all", "value": float(0.0 if len(catalog) == 0 else len(matched_ids) / len(catalog))},
        {
            "metric": "catalog_fraction_with_mecha_local_zone",
            "value": float(0.0 if catalog["within_60km_either_m1_m3"].sum() == 0 else len(set(catalog.loc[catalog["within_60km_either_m1_m3"] & catalog["event_id"].isin(matched_ids), "event_id"])) / catalog["within_60km_either_m1_m3"].sum()),
        },
        {"metric": "best_match_time_tol_sec", "value": float(config.time_tol_sec)},
        {"metric": "best_match_horizontal_tol_km", "value": float(config.horizontal_tol_km)},
        {"metric": "best_match_depth_tol_km", "value": float(config.depth_tol_km)},
    ]
    if not matches.empty:
        metrics.extend([
            {"metric": "median_match_time_diff_sec", "value": float(matches["time_diff_sec"].median())},
            {"metric": "median_match_horizontal_diff_km", "value": float(matches["horizontal_diff_km"].median())},
            {"metric": "median_match_depth_diff_km", "value": float(matches["depth_diff_km"].median())},
            {"metric": "p95_match_time_diff_sec", "value": float(matches["time_diff_sec"].quantile(0.95))},
            {"metric": "p95_match_horizontal_diff_km", "value": float(matches["horizontal_diff_km"].quantile(0.95))},
            {"metric": "p95_match_depth_diff_km", "value": float(matches["depth_diff_km"].quantile(0.95))},
        ])
    top_row = tolerance_df.iloc[0]
    metrics.extend([
        {"metric": "top_grid_matched_fraction", "value": float(top_row["matched_fraction"])},
        {"metric": "top_grid_candidate_pairs", "value": float(top_row["candidate_pairs"])},
        {"metric": "top_grid_ambiguous_mecha_rows", "value": float(top_row["ambiguous_mecha_rows"])},
        {"metric": "top_grid_ambiguous_catalog_events", "value": float(top_row["ambiguous_catalog_events"])},
    ])
    return pd.DataFrame(metrics)


def coverage_for_group(catalog_subset: pd.DataFrame, matched_subset: pd.DataFrame, label_fields: Dict[str, object]) -> Dict[str, object]:
    out = dict(label_fields)
    total_events = int(len(catalog_subset))
    matched_events = int(matched_subset["catalog_event_id"].nunique())
    out["catalog_event_count"] = total_events
    out["matched_event_count"] = matched_events
    out["coverage_fraction"] = np.nan if total_events == 0 else matched_events / total_events
    if matched_subset.empty:
        out["complete_mechanism_count"] = 0
        out["partial_mechanism_count"] = 0
        out["metadata_only_count"] = 0
        out["complete_mechanism_fraction_of_matched"] = np.nan
        out["median_match_time_diff_sec"] = np.nan
        out["median_match_horizontal_diff_km"] = np.nan
        out["median_match_depth_diff_km"] = np.nan
        out["median_catalog_mag_of_matched"] = np.nan
        return out
    detail_counts = matched_subset["mechanism_detail_class"].value_counts()
    out["complete_mechanism_count"] = int(detail_counts.get("complete_mechanism", 0))
    out["partial_mechanism_count"] = int(detail_counts.get("partial_mechanism", 0))
    out["metadata_only_count"] = int(detail_counts.get("metadata_only", 0))
    out["complete_mechanism_fraction_of_matched"] = out["complete_mechanism_count"] / matched_events if matched_events > 0 else np.nan
    out["median_match_time_diff_sec"] = float(matched_subset["time_diff_sec"].median())
    out["median_match_horizontal_diff_km"] = float(matched_subset["horizontal_diff_km"].median())
    out["median_match_depth_diff_km"] = float(matched_subset["depth_diff_km"].median())
    out["median_catalog_mag_of_matched"] = float(matched_subset["catalog_mag"].median())
    return out


def build_phase_coverage(catalog: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for phase in PHASE_ORDER:
        cat_sub = catalog[catalog["phase_primary"] == phase]
        matched_sub = matched[matched["phase_primary"] == phase]
        rows.append(coverage_for_group(cat_sub, matched_sub, {"phase_primary": phase}))
    return pd.DataFrame(rows)


def build_spatial_coverage(catalog: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for subset_name, col in SPATIAL_CLASSES:
        cat_sub = catalog[catalog[col].fillna(False)]
        matched_sub = matched[matched[col].fillna(False)]
        rows.append(coverage_for_group(cat_sub, matched_sub, {"spatial_class": subset_name, "spatial_flag_column": col}))
    return pd.DataFrame(rows)


def build_phase_spatial_coverage(catalog: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    priority_subsets = ["combined_local", "M1_extended", "M3_extended", "along_axis_30km", "off_axis_30km"]
    subset_map = {name: col for name, col in SPATIAL_CLASSES if name in priority_subsets}
    for phase in PHASE_ORDER:
        for subset_name, col in subset_map.items():
            cat_sub = catalog[(catalog["phase_primary"] == phase) & (catalog[col].fillna(False))]
            matched_sub = matched[(matched["phase_primary"] == phase) & (matched[col].fillna(False))]
            rows.append(coverage_for_group(cat_sub, matched_sub, {"phase_primary": phase, "spatial_class": subset_name}))
    return pd.DataFrame(rows)


def build_magnitude_representativeness(catalog: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for thr in REPRESENTATIVE_MAG_THRESHOLDS:
        cat_sub = catalog[catalog["mag"] >= thr]
        matched_sub = matched[matched["catalog_mag"] >= thr]
        row = coverage_for_group(cat_sub, matched_sub, {"mag_threshold": thr})
        if len(cat_sub) > 0 and len(matched_sub) > 0:
            row["catalog_median_depth_km"] = float(cat_sub["depth_km"].median())
            row["matched_median_depth_km"] = float(matched_sub["catalog_depth_km"].median())
            row["catalog_median_dist_m1_km"] = float(cat_sub["dist_m1_km"].median()) if "dist_m1_km" in cat_sub.columns else np.nan
            row["matched_median_dist_m1_km"] = float(matched_sub["dist_m1_km"].median()) if "dist_m1_km" in matched_sub.columns else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def build_phase_mag_coverage(catalog: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for phase in PHASE_ORDER:
        cat_phase = catalog[catalog["phase_primary"] == phase]
        matched_phase = matched[matched["phase_primary"] == phase]
        for thr in REPRESENTATIVE_MAG_THRESHOLDS:
            rows.append(
                coverage_for_group(
                    cat_phase[cat_phase["mag"] >= thr],
                    matched_phase[matched_phase["catalog_mag"] >= thr],
                    {"phase_primary": phase, "mag_threshold": thr},
                )
            )
    return pd.DataFrame(rows)


def build_representativeness_tests(catalog: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    matched_ids = set(matched["catalog_event_id"].astype(int).tolist()) if not matched.empty else set()
    catalog = catalog.copy()
    catalog["has_mecha_match"] = catalog["event_id"].isin(matched_ids)

    def add_test(group_name: str, mask: pd.Series, variable: str) -> None:
        sub = catalog.loc[mask, [variable, "has_mecha_match"]].dropna()
        if sub.empty:
            rows.append({"group_name": group_name, "variable": variable, "n_total": 0, "n_matched": 0, "matched_median": np.nan, "unmatched_median": np.nan, "median_difference": np.nan})
            return
        matched_vals = sub.loc[sub["has_mecha_match"], variable]
        unmatched_vals = sub.loc[~sub["has_mecha_match"], variable]
        rows.append(
            {
                "group_name": group_name,
                "variable": variable,
                "n_total": int(len(sub)),
                "n_matched": int(len(matched_vals)),
                "matched_median": float(matched_vals.median()) if len(matched_vals) > 0 else np.nan,
                "unmatched_median": float(unmatched_vals.median()) if len(unmatched_vals) > 0 else np.nan,
                "median_difference": float(matched_vals.median() - unmatched_vals.median()) if len(matched_vals) > 0 and len(unmatched_vals) > 0 else np.nan,
            }
        )

    add_test("all_catalog", pd.Series(True, index=catalog.index), "mag")
    add_test("combined_local", catalog["within_60km_either_m1_m3"].fillna(False), "mag")
    add_test("combined_local", catalog["within_60km_either_m1_m3"].fillna(False), "depth_km")
    add_test("combined_local", catalog["within_60km_either_m1_m3"].fillna(False), "dist_m1_km")
    add_test("combined_local", catalog["within_60km_either_m1_m3"].fillna(False), "dist_m3_km")
    for phase in ["baseline_to_M1_minus14d", "M1_related_M1minus14d_to_M1plus21d", "middle_M1plus21d_to_M3minus35d", "preM3_M3minus35d_to_M3", "post_M3_context"]:
        phase_mask = catalog["phase_primary"] == phase
        add_test(f"phase::{phase}", phase_mask, "mag")
        add_test(f"phase::{phase}", phase_mask, "depth_km")
    return pd.DataFrame(rows)


def build_mechanism_field_completeness(mecha: pd.DataFrame, matched: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "mag_1", "mag_2", "focal_mech_score", "n_mech_stations", "P_axis_azimuth", "T_axis_azimuth",
        "strike_plane1", "dip_plane1", "rake_plane1", "strike_plane2", "dip_plane2", "rake_plane2",
        "focal_mech_projection", "m_method", "m_source",
    ]
    rows: List[Dict[str, object]] = []
    for dataset_name, df in [("all_mecha_rows", mecha), ("matched_mecha_rows", matched)]:
        n = len(df)
        for field in fields:
            if field not in df.columns:
                continue
            non_null = int(df[field].notna().sum())
            rows.append({
                "dataset_name": dataset_name,
                "field_name": field,
                "row_count": n,
                "non_null_count": non_null,
                "non_null_fraction": np.nan if n == 0 else non_null / n,
            })
    return pd.DataFrame(rows)


def build_summary_text(overall: pd.DataFrame, phase_cov: pd.DataFrame, spatial_cov: pd.DataFrame, mag_cov: pd.DataFrame, rep_tests: pd.DataFrame) -> str:
    metrics = dict(zip(overall["metric"], overall["value"]))
    local_cov = spatial_cov.loc[spatial_cov["spatial_class"] == "combined_local"].iloc[0] if not spatial_cov.empty and (spatial_cov["spatial_class"] == "combined_local").any() else None
    m1_cov = spatial_cov.loc[spatial_cov["spatial_class"] == "M1_extended"].iloc[0] if not spatial_cov.empty and (spatial_cov["spatial_class"] == "M1_extended").any() else None
    m3_cov = spatial_cov.loc[spatial_cov["spatial_class"] == "M3_extended"].iloc[0] if not spatial_cov.empty and (spatial_cov["spatial_class"] == "M3_extended").any() else None
    pre_m3 = phase_cov.loc[phase_cov["phase_primary"] == "preM3_M3minus35d_to_M3"].iloc[0] if not phase_cov.empty and (phase_cov["phase_primary"] == "preM3_M3minus35d_to_M3").any() else None
    m1_phase = phase_cov.loc[phase_cov["phase_primary"] == "M1_related_M1minus14d_to_M1plus21d"].iloc[0] if not phase_cov.empty and (phase_cov["phase_primary"] == "M1_related_M1minus14d_to_M1plus21d").any() else None
    mag45 = mag_cov.loc[np.isclose(mag_cov["mag_threshold"], 4.5)].iloc[0] if not mag_cov.empty and np.isclose(mag_cov["mag_threshold"], 4.5).any() else None
    rep_mag_local = rep_tests.loc[(rep_tests["group_name"] == "combined_local") & (rep_tests["variable"] == "mag")].iloc[0] if not rep_tests.empty and ((rep_tests["group_name"] == "combined_local") & (rep_tests["variable"] == "mag")).any() else None

    lines = [
        "Mechanism coverage audit summary",
        f"- Matched {int(metrics.get('matched_mecha_rows', 0))} mechanism rows out of {int(metrics.get('mecha_total_rows', 0))} metadata rows ({metrics.get('matched_fraction_of_mecha_rows', float('nan')):.3f}).",
        f"- Best reusable matching tolerances: time <= {metrics.get('best_match_time_tol_sec', float('nan')):.1f} s, horizontal <= {metrics.get('best_match_horizontal_tol_km', float('nan')):.1f} km, depth <= {metrics.get('best_match_depth_tol_km', float('nan')):.1f} km.",
        f"- Catalog-wide coverage is sparse: {metrics.get('catalog_fraction_with_mecha_all', float('nan')):.4f} of all relocated events and {metrics.get('catalog_fraction_with_mecha_local_zone', float('nan')):.4f} of the combined local-zone events have a matched mechanism row.",
    ]
    if local_cov is not None:
        lines.append(f"- Combined local-zone matched-event coverage = {local_cov['coverage_fraction']:.4f} ({int(local_cov['matched_event_count'])}/{int(local_cov['catalog_event_count'])}); complete-mechanism fraction among matched local events = {local_cov['complete_mechanism_fraction_of_matched']:.3f}.")
    if m1_cov is not None and m3_cov is not None:
        lines.append(f"- Extended-zone coverage comparison: M1-extended = {m1_cov['coverage_fraction']:.4f}, M3-extended = {m3_cov['coverage_fraction']:.4f}; differences should be treated as descriptive because both samples are sparse.")
    if m1_phase is not None and pre_m3 is not None:
        lines.append(f"- Phase coverage comparison: M1-related phase = {m1_phase['coverage_fraction']:.4f}, pre-M3 phase = {pre_m3['coverage_fraction']:.4f}; low fractions imply mechanism consistency by phase is exploratory unless restricted to larger events.")
    if mag45 is not None:
        lines.append(f"- Coverage rises strongly with magnitude: for M>=4.5 events the matched fraction is {mag45['coverage_fraction']:.3f} ({int(mag45['matched_event_count'])}/{int(mag45['catalog_event_count'])}).")
    if rep_mag_local is not None and pd.notna(rep_mag_local['median_difference']):
        lines.append(f"- Representativeness check in the combined local zone: matched events have median magnitude {rep_mag_local['matched_median']:.2f} versus {rep_mag_local['unmatched_median']:.2f} for unmatched events (difference {rep_mag_local['median_difference']:.2f}), indicating strong magnitude-biased mechanism availability.")
    lines.extend([
        "- Interpretation rule: focal mechanisms should be considered unavailable for general catalog-wide phase/spatial inference, and only exploratory-to-descriptive for larger-event subsets with explicitly reported coverage.",
        "- This audit addresses metadata matching and sampling bias only; it does not justify physical interpretation of rupture style or triggering.",
    ])
    return "\n".join(lines) + "\n"


def plot_phase_spatial_heatmaps(phase_cov: pd.DataFrame, spatial_cov: pd.DataFrame, mag_cov: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)

    phase_plot = phase_cov.copy()
    phase_plot["phase_primary"] = pd.Categorical(phase_plot["phase_primary"], categories=PHASE_ORDER, ordered=True)
    phase_plot = phase_plot.sort_values("phase_primary")
    sns.barplot(data=phase_plot, x="phase_primary", y="coverage_fraction", color="#4C78A8", ax=axes[0])
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].set_xlabel("Phase")
    axes[0].set_ylabel("Matched fraction")
    axes[0].set_title("Mechanism coverage by phase")

    spatial_plot = spatial_cov.copy().sort_values("coverage_fraction", ascending=False)
    sns.barplot(data=spatial_plot, y="spatial_class", x="coverage_fraction", color="#F58518", ax=axes[1])
    axes[1].set_xlabel("Matched fraction")
    axes[1].set_ylabel("Spatial class")
    axes[1].set_title("Mechanism coverage by spatial class")

    mag_plot = mag_cov.copy().sort_values("mag_threshold")
    sns.lineplot(data=mag_plot, x="mag_threshold", y="coverage_fraction", marker="o", ax=axes[2], color="#54A24B")
    axes[2].set_xlabel("Catalog magnitude threshold")
    axes[2].set_ylabel("Matched fraction")
    axes[2].set_title("Coverage increases with magnitude")
    axes[2].set_ylim(bottom=0)

    fig.savefig(OUTPUT_DIR / "mechanism_coverage_overview.png", dpi=220)
    plt.close(fig)


def plot_representativeness(rep_tests: pd.DataFrame) -> None:
    plot_df = rep_tests[rep_tests["variable"].isin(["mag", "depth_km"])].copy()
    if plot_df.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    plot_df["label"] = plot_df["group_name"] + " | " + plot_df["variable"]
    sns.barplot(data=plot_df, y="label", x="median_difference", color="#B279A2", ax=ax)
    ax.axvline(0.0, color="k", linewidth=1)
    ax.set_xlabel("Matched minus unmatched median")
    ax.set_ylabel("Group | variable")
    ax.set_title("Representativeness bias diagnostics")
    fig.savefig(OUTPUT_DIR / "mechanism_representativeness_bias.png", dpi=220)
    plt.close(fig)


def plot_field_completeness(field_comp: pd.DataFrame) -> None:
    plot_df = field_comp[field_comp["dataset_name"] == "matched_mecha_rows"].copy()
    if plot_df.empty:
        return
    plot_df = plot_df.sort_values("non_null_fraction", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    sns.barplot(data=plot_df, y="field_name", x="non_null_fraction", color="#E45756", ax=ax)
    ax.set_xlabel("Non-null fraction among matched mechanism rows")
    ax.set_ylabel("Field")
    ax.set_title("Mechanism-field completeness among matched rows")
    fig.savefig(OUTPUT_DIR / "mechanism_field_completeness.png", dpi=220)
    plt.close(fig)


def main() -> None:
    ensure_output_dir()
    log(f"Script path: {SCRIPT_PATH}")
    log(f"Output directory: {OUTPUT_DIR}")

    catalog = load_catalog_with_fallback()
    mecha = load_mechanisms()
    _ = load_mainshocks()

    tolerance_df, matches_basic, config = run_tolerance_grid(catalog, mecha)
    matched = merge_match_context(catalog, mecha, matches_basic)

    overall = summarize_matching(catalog, mecha, matched, config, tolerance_df)
    phase_cov = build_phase_coverage(catalog, matched)
    spatial_cov = build_spatial_coverage(catalog, matched)
    phase_spatial_cov = build_phase_spatial_coverage(catalog, matched)
    mag_cov = build_magnitude_representativeness(catalog, matched)
    phase_mag_cov = build_phase_mag_coverage(catalog, matched)
    rep_tests = build_representativeness_tests(catalog, matched)
    field_comp = build_mechanism_field_completeness(mecha, matched)

    tolerance_df.to_csv(OUTPUT_DIR / "mechanism_matching_tolerance_grid.csv", index=False)
    matches_basic.to_csv(OUTPUT_DIR / "mechanism_match_pairs_basic.csv", index=False)
    matched.to_csv(OUTPUT_DIR / "mechanism_match_pairs_with_context.csv", index=False)
    overall.to_csv(OUTPUT_DIR / "mechanism_coverage_audit.csv", index=False)
    phase_cov.to_csv(OUTPUT_DIR / "mechanism_coverage_by_phase.csv", index=False)
    spatial_cov.to_csv(OUTPUT_DIR / "mechanism_coverage_by_spatial_class.csv", index=False)
    phase_spatial_cov.to_csv(OUTPUT_DIR / "mechanism_coverage_by_phase_and_spatial_class.csv", index=False)
    mag_cov.to_csv(OUTPUT_DIR / "mechanism_coverage_by_magnitude_threshold.csv", index=False)
    phase_mag_cov.to_csv(OUTPUT_DIR / "mechanism_coverage_by_phase_and_magnitude.csv", index=False)
    rep_tests.to_csv(OUTPUT_DIR / "mechanism_representativeness_tests.csv", index=False)
    field_comp.to_csv(OUTPUT_DIR / "mechanism_field_completeness.csv", index=False)

    summary_text = build_summary_text(overall, phase_cov, spatial_cov, mag_cov, rep_tests)
    (OUTPUT_DIR / "mechanism_coverage_summary.txt").write_text(summary_text, encoding="utf-8")

    plot_phase_spatial_heatmaps(phase_cov, spatial_cov, mag_cov)
    plot_representativeness(rep_tests)
    plot_field_completeness(field_comp)

    log("Mechanism coverage audit completed successfully")
    log(summary_text)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
