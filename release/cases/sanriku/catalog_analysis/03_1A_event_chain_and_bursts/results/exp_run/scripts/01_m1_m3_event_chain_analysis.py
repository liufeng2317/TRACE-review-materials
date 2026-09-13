from __future__ import annotations

import math
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>")
RUN_DIR = BASE_DIR / "run" / "03_1A_event_chain_and_bursts" / "exp_run"
OUTPUT_DIR = RUN_DIR / "outputs" / "01_m1_m3_event_chain_analysis"
CATALOG_PATH = BASE_DIR / "data" / "catalog" / "Snet_catalog_relocate_250601_260501.csv"
MAINSHOCK_PATH = BASE_DIR / "data" / "catalog" / "main_earthquake.csv"
MECHA_PATH = BASE_DIR / "data" / "source_mechanism" / "Snet_mecha.csv"

CATALOG_COLUMNS = ["origin_time", "latitude", "longitude", "depth_km", "magnitude"]
MAG_THRESHOLDS = [3.0, 4.0, 5.0, 6.0]
PRIMARY_CORRIDOR_WIDTH_KM = 20.0
SENSITIVITY_CORRIDOR_WIDTH_KM = 30.0
CORE_RADIUS_KM = 30.0
EXTENDED_RADIUS_KM = 60.0
M2_RADIUS_KM = 100.0
EARTH_RADIUS_KM = 6371.0
POST_M3_WINDOWS_DAYS = [7, 14]
ROLLING_BURST_WINDOWS = [1, 3, 7]
MIN_BURST_EVENTS = {3.0: 4, 4.0: 2}


@dataclass(frozen=True)
class Mainshock:
    label: str
    origin_time: pd.Timestamp
    latitude: float
    longitude: float
    depth_km: float
    magnitude: float


WINDOW_DEFINITIONS = {
    "pre_M1_baseline_14d": ("-inf", "M1-14d"),
    "pre_M1_baseline_7d": ("-inf", "M1-7d"),
    "M1_related_primary": ("M1-14d", "M1+21d"),
    "M1_related_sensitivity_narrow": ("M1-7d", "M1+14d"),
    "M1_related_sensitivity_broad": ("M1-14d", "M1+28d"),
    "full_M1_to_M3": ("M1", "M3"),
    "middle_primary": ("M1+21d", "M3-35d"),
    "pre_M3_primary": ("M3-35d", "M3"),
    "pre_M3_sensitivity_42d": ("M3-42d", "M3"),
    "pre_M3_sensitivity_28d": ("M3-28d", "M3"),
    "post_M3_7d": ("M3", "M3+7d"),
    "post_M3_14d": ("M3", "M3+14d"),
}


def log(message: str) -> None:
    print(message, flush=True)


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def local_xy_km(lat, lon, ref_lat, ref_lon):
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    lat0 = float(ref_lat)
    lon0 = float(ref_lon)
    x = (lon - lon0) * 111.32 * math.cos(math.radians(lat0))
    y = (lat - lat0) * 110.574
    return x, y


def parse_bound(token: str, refs: Dict[str, Mainshock]) -> pd.Timestamp | None:
    token = token.strip()
    if token == "-inf":
        return None
    if token in refs:
        return refs[token].origin_time
    if "+" in token:
        key, offset = token.split("+", 1)
        return refs[key].origin_time + pd.to_timedelta(offset)
    if "-" in token:
        key, offset = token.split("-", 1)
        return refs[key].origin_time - pd.to_timedelta(offset)
    raise ValueError(f"Unsupported time token: {token}")


def format_threshold_label(threshold: float) -> str:
    return f"M{int(threshold)}+"


def clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    removable = [
        "m1_m3_event_chain_table.csv",
        "m1_m3_reference_table.csv",
        "m1_m3_window_summary_counts_rates.csv",
        "m1_m3_window_summary_composition.csv",
        "m1_m3_raw_vs_m2aware_summary.csv",
        "m1_m3_phase_contribution_summary.csv",
        "m1_m3_burst_table.csv",
        "m1_m3_gap_continuity_metrics.csv",
        "m1_m3_migration_endpoint_switching_summary.csv",
        "m1_m3_control_comparison.csv",
        "m1_m3_followup_targets.csv",
        "m1_m3_classification_summary.csv",
    ]
    for name in removable:
        path = output_dir / name
        if path.exists():
            path.unlink()


def load_mainshocks(path: Path) -> Dict[str, Mainshock]:
    log(f"Loading mainshock table: {path}")
    df = pd.read_csv(path)
    rename_map = {"index": "label", "datetime": "origin_time", "lat": "latitude", "lon": "longitude", "dep": "depth_km", "mag": "magnitude"}
    df = df.rename(columns=rename_map)
    required = ["label", "origin_time", "latitude", "longitude", "depth_km", "magnitude"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Mainshock table missing columns: {missing}")
    df["origin_time"] = pd.to_datetime(df["origin_time"], utc=True)
    refs = {}
    for _, row in df.iterrows():
        refs[str(row["label"])] = Mainshock(
            label=str(row["label"]),
            origin_time=row["origin_time"],
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            depth_km=float(row["depth_km"]),
            magnitude=float(row["magnitude"]),
        )
    for key in ["M1", "M2", "M3"]:
        if key not in refs:
            raise ValueError(f"Mainshock table does not contain required label {key}")
    return refs


def load_catalog(path: Path) -> pd.DataFrame:
    log(f"Loading relocated catalog: {path}")
    df = pd.read_csv(path, header=None, names=CATALOG_COLUMNS)
    df["origin_time"] = pd.to_datetime(df["origin_time"], utc=True)
    numeric_cols = ["latitude", "longitude", "depth_km", "magnitude"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["origin_time", "latitude", "longitude", "depth_km", "magnitude"]).copy()
    df = df.sort_values("origin_time").reset_index(drop=True)
    df["event_id"] = [f"evt_{i:06d}" for i in range(1, len(df) + 1)]
    return df


def build_geometry(df: pd.DataFrame, refs: Dict[str, Mainshock]) -> pd.DataFrame:
    m1, m2, m3 = refs["M1"], refs["M2"], refs["M3"]
    lat0 = (m1.latitude + m3.latitude) / 2.0
    lon0 = (m1.longitude + m3.longitude) / 2.0
    event_x, event_y = local_xy_km(df["latitude"].to_numpy(), df["longitude"].to_numpy(), lat0, lon0)
    m1x, m1y = local_xy_km([m1.latitude], [m1.longitude], lat0, lon0)
    m3x, m3y = local_xy_km([m3.latitude], [m3.longitude], lat0, lon0)
    m1x, m1y, m3x, m3y = float(m1x[0]), float(m1y[0]), float(m3x[0]), float(m3y[0])
    axis_vec = np.array([m3x - m1x, m3y - m1y], dtype=float)
    axis_len = float(np.hypot(axis_vec[0], axis_vec[1]))
    axis_hat = axis_vec / axis_len
    rel_x = event_x - m1x
    rel_y = event_y - m1y
    along = rel_x * axis_hat[0] + rel_y * axis_hat[1]
    perp = np.abs(rel_x * axis_hat[1] - rel_y * axis_hat[0])
    dist_m1 = haversine_km(df["latitude"].to_numpy(), df["longitude"].to_numpy(), m1.latitude, m1.longitude)
    dist_m2 = haversine_km(df["latitude"].to_numpy(), df["longitude"].to_numpy(), m2.latitude, m2.longitude)
    dist_m3 = haversine_km(df["latitude"].to_numpy(), df["longitude"].to_numpy(), m3.latitude, m3.longitude)
    df = df.copy()
    df["time_since_M1_days"] = (df["origin_time"] - m1.origin_time) / pd.Timedelta(days=1)
    df["time_before_M3_days"] = (m3.origin_time - df["origin_time"]) / pd.Timedelta(days=1)
    df["distance_to_M1_km"] = dist_m1
    df["distance_to_M2_km"] = dist_m2
    df["distance_to_M3_km"] = dist_m3
    df["along_axis_km"] = along
    df["perpendicular_distance_km"] = perp
    df["axis_length_km"] = axis_len
    df["axis_fraction"] = along / axis_len
    df["nearest_endpoint"] = np.where(dist_m1 <= dist_m3, "M1", "M3")
    df["in_M1_core_30km"] = dist_m1 <= CORE_RADIUS_KM
    df["in_M3_core_30km"] = dist_m3 <= CORE_RADIUS_KM
    df["in_M1_extended_60km"] = dist_m1 <= EXTENDED_RADIUS_KM
    df["in_M3_extended_60km"] = dist_m3 <= EXTENDED_RADIUS_KM
    df["in_local_union_60km"] = df["in_M1_extended_60km"] | df["in_M3_extended_60km"]
    corridor_buffer = EXTENDED_RADIUS_KM
    corridor_between = (along >= -corridor_buffer) & (along <= axis_len + corridor_buffer)
    df["in_corridor_20km"] = corridor_between & (perp <= PRIMARY_CORRIDOR_WIDTH_KM)
    df["in_corridor_30km"] = corridor_between & (perp <= SENSITIVITY_CORRIDOR_WIDTH_KM)
    df["off_corridor_local"] = df["in_local_union_60km"] & (~df["in_corridor_20km"])
    df["M2_related_100km"] = dist_m2 <= M2_RADIUS_KM
    df["M2_ambiguous_overlap"] = df["M2_related_100km"] & (df["in_local_union_60km"] | df["in_corridor_20km"])

    categories = np.full(len(df), "outside_local_union", dtype=object)
    overlap_core = df["in_M1_core_30km"] & df["in_M3_core_30km"]
    m1_core = df["in_M1_core_30km"] & ~df["in_M3_core_30km"]
    m3_core = df["in_M3_core_30km"] & ~df["in_M1_core_30km"]
    corridor_noncore = df["in_local_union_60km"] & df["in_corridor_20km"] & ~(df["in_M1_core_30km"] | df["in_M3_core_30km"])
    off_corr = df["in_local_union_60km"] & ~df["in_corridor_20km"] & ~(df["in_M1_core_30km"] | df["in_M3_core_30km"])
    categories[overlap_core] = "overlap_core"
    categories[m1_core] = "M1-core"
    categories[m3_core] = "M3-core"
    categories[corridor_noncore] = "corridor_noncore"
    categories[off_corr] = "off-corridor_local"
    df["spatial_category"] = categories
    return df


def assign_windows(df: pd.DataFrame, refs: Dict[str, Mainshock]) -> pd.DataFrame:
    df = df.copy()
    for window_name, (start_token, end_token) in WINDOW_DEFINITIONS.items():
        start = parse_bound(start_token, refs)
        end = parse_bound(end_token, refs)
        mask = pd.Series(True, index=df.index)
        if start is not None:
            mask &= df["origin_time"] >= start
        if end is not None:
            mask &= df["origin_time"] < end
        df[f"window__{window_name}"] = mask
    return df


def build_reference_table(refs: Dict[str, Mainshock]) -> pd.DataFrame:
    rows = []
    m1, m2, m3 = refs["M1"], refs["M2"], refs["M3"]
    for item in [m1, m2, m3]:
        rows.append(
            {
                "label": item.label,
                "origin_time": item.origin_time,
                "latitude": item.latitude,
                "longitude": item.longitude,
                "depth_km": item.depth_km,
                "magnitude": item.magnitude,
                "distance_to_M1_km": haversine_km(item.latitude, item.longitude, m1.latitude, m1.longitude),
                "distance_to_M2_km": haversine_km(item.latitude, item.longitude, m2.latitude, m2.longitude),
                "distance_to_M3_km": haversine_km(item.latitude, item.longitude, m3.latitude, m3.longitude),
            }
        )
    return pd.DataFrame(rows)


def get_window_duration_days(df: pd.DataFrame, mask: pd.Series) -> float:
    sub = df.loc[mask, "origin_time"]
    if sub.empty:
        return 0.0
    duration = (sub.max() - sub.min()) / pd.Timedelta(days=1)
    return float(max(duration, 1e-9))


def summarize_counts_rates(chain_df: pd.DataFrame, refs: Dict[str, Mainshock]) -> pd.DataFrame:
    log("Computing counts/rates summary")
    rows: List[Dict[str, object]] = []
    total_full_raw = {}
    total_full_m2 = {}
    full_mask = chain_df["window__full_M1_to_M3"]
    for threshold in MAG_THRESHOLDS:
        mag_mask = chain_df["magnitude"] >= threshold
        total_full_raw[threshold] = int((full_mask & mag_mask).sum())
        total_full_m2[threshold] = int((full_mask & mag_mask & ~chain_df["M2_related_100km"]).sum())
    for window_name in WINDOW_DEFINITIONS:
        mask_window = chain_df[f"window__{window_name}"]
        duration_days = get_window_duration_days(chain_df, mask_window)
        for version_name, version_mask in {
            "raw": pd.Series(True, index=chain_df.index),
            "m2aware": ~chain_df["M2_related_100km"],
        }.items():
            final_mask = mask_window & version_mask
            for threshold in MAG_THRESHOLDS:
                mag_mask = chain_df["magnitude"] >= threshold
                count = int((final_mask & mag_mask).sum())
                base_total = total_full_raw[threshold] if version_name == "raw" else total_full_m2[threshold]
                fraction = count / base_total if base_total > 0 else np.nan
                rows.append(
                    {
                        "window": window_name,
                        "version": version_name,
                        "magnitude_threshold": threshold,
                        "threshold_label": format_threshold_label(threshold),
                        "event_count": count,
                        "duration_days": duration_days,
                        "rate_per_day": count / duration_days if duration_days > 0 else np.nan,
                        "fraction_of_full_M1_to_M3": fraction,
                        "window_start": parse_bound(WINDOW_DEFINITIONS[window_name][0], refs),
                        "window_end": parse_bound(WINDOW_DEFINITIONS[window_name][1], refs),
                    }
                )
    return pd.DataFrame(rows)


def summarize_composition(chain_df: pd.DataFrame, refs: Dict[str, Mainshock]) -> pd.DataFrame:
    log("Computing window composition summary")
    spatial_categories = ["overlap_core", "M1-core", "M3-core", "corridor_noncore", "off-corridor_local"]
    rows = []
    local_mask = chain_df["in_local_union_60km"]
    for window_name in WINDOW_DEFINITIONS:
        mask_window = chain_df[f"window__{window_name}"]
        for version_name, version_mask in {
            "raw": pd.Series(True, index=chain_df.index),
            "m2aware": ~chain_df["M2_related_100km"],
        }.items():
            final_mask = mask_window & version_mask & local_mask
            total_local = int(final_mask.sum())
            row_base = {
                "window": window_name,
                "version": version_name,
                "window_start": parse_bound(WINDOW_DEFINITIONS[window_name][0], refs),
                "window_end": parse_bound(WINDOW_DEFINITIONS[window_name][1], refs),
                "total_local_events": total_local,
                "count_in_M1_extended_60km": int((mask_window & version_mask & chain_df["in_M1_extended_60km"]).sum()),
                "count_in_M3_extended_60km": int((mask_window & version_mask & chain_df["in_M3_extended_60km"]).sum()),
                "count_in_corridor_20km": int((mask_window & version_mask & chain_df["in_corridor_20km"]).sum()),
                "count_in_corridor_30km": int((mask_window & version_mask & chain_df["in_corridor_30km"]).sum()),
            }
            m1_core_count = int((final_mask & (chain_df["spatial_category"] == "M1-core")).sum())
            m3_core_count = int((final_mask & (chain_df["spatial_category"] == "M3-core")).sum())
            row_base["M1_core_minus_M3_core"] = m1_core_count - m3_core_count
            row_base["M1_to_M3_core_ratio"] = (m1_core_count / m3_core_count) if m3_core_count > 0 else np.nan
            for cat in spatial_categories:
                count = int((final_mask & (chain_df["spatial_category"] == cat)).sum())
                row_base[f"count_{cat}"] = count
                row_base[f"fraction_{cat}"] = count / total_local if total_local > 0 else np.nan
            rows.append(row_base)
    return pd.DataFrame(rows)


def summarize_raw_vs_m2aware(counts_df: pd.DataFrame, composition_df: pd.DataFrame) -> pd.DataFrame:
    log("Computing raw vs M2-aware summary")
    rows = []
    merged_counts = counts_df.pivot_table(
        index=["window", "magnitude_threshold", "threshold_label"],
        columns="version",
        values=["event_count", "rate_per_day", "fraction_of_full_M1_to_M3"],
        aggfunc="first",
    )
    merged_counts.columns = ["__".join(map(str, c)).strip() for c in merged_counts.columns.to_flat_index()]
    merged_counts = merged_counts.reset_index()
    for _, row in merged_counts.iterrows():
        raw_count = row.get("event_count__raw", np.nan)
        m2_count = row.get("event_count__m2aware", np.nan)
        rows.append(
            {
                "summary_type": "counts_rates",
                "window": row["window"],
                "magnitude_threshold": row["magnitude_threshold"],
                "threshold_label": row["threshold_label"],
                "raw_event_count": raw_count,
                "m2aware_event_count": m2_count,
                "count_difference_raw_minus_m2aware": raw_count - m2_count if pd.notna(raw_count) and pd.notna(m2_count) else np.nan,
                "fraction_removed_by_M2": (raw_count - m2_count) / raw_count if pd.notna(raw_count) and raw_count not in (0, np.nan) else np.nan,
                "raw_rate_per_day": row.get("rate_per_day__raw", np.nan),
                "m2aware_rate_per_day": row.get("rate_per_day__m2aware", np.nan),
                "raw_fraction_of_full": row.get("fraction_of_full_M1_to_M3__raw", np.nan),
                "m2aware_fraction_of_full": row.get("fraction_of_full_M1_to_M3__m2aware", np.nan),
            }
        )
    comp_subset = composition_df[["window", "version", "total_local_events", "count_M1-core", "count_M3-core", "count_corridor_noncore", "count_off-corridor_local"]].copy()
    comp_pivot = comp_subset.pivot_table(index="window", columns="version", values=[c for c in comp_subset.columns if c not in ["window", "version"]], aggfunc="first")
    comp_pivot.columns = ["__".join(map(str, c)).strip() for c in comp_pivot.columns.to_flat_index()]
    comp_pivot = comp_pivot.reset_index()
    for _, row in comp_pivot.iterrows():
        raw_total = row.get("total_local_events__raw", np.nan)
        m2_total = row.get("total_local_events__m2aware", np.nan)
        rows.append(
            {
                "summary_type": "composition",
                "window": row["window"],
                "magnitude_threshold": np.nan,
                "threshold_label": "all_magnitudes",
                "raw_event_count": raw_total,
                "m2aware_event_count": m2_total,
                "count_difference_raw_minus_m2aware": raw_total - m2_total if pd.notna(raw_total) and pd.notna(m2_total) else np.nan,
                "fraction_removed_by_M2": (raw_total - m2_total) / raw_total if pd.notna(raw_total) and raw_total not in (0, np.nan) else np.nan,
                "raw_rate_per_day": np.nan,
                "m2aware_rate_per_day": np.nan,
                "raw_fraction_of_full": np.nan,
                "m2aware_fraction_of_full": np.nan,
                "raw_M1_core": row.get("count_M1-core__raw", np.nan),
                "raw_M3_core": row.get("count_M3-core__raw", np.nan),
                "raw_corridor_noncore": row.get("count_corridor_noncore__raw", np.nan),
                "raw_off_corridor_local": row.get("count_off-corridor_local__raw", np.nan),
                "m2aware_M1_core": row.get("count_M1-core__m2aware", np.nan),
                "m2aware_M3_core": row.get("count_M3-core__m2aware", np.nan),
                "m2aware_corridor_noncore": row.get("count_corridor_noncore__m2aware", np.nan),
                "m2aware_off_corridor_local": row.get("count_off-corridor_local__m2aware", np.nan),
            }
        )
    return pd.DataFrame(rows)


def summarize_phase_contributions(counts_df: pd.DataFrame) -> pd.DataFrame:
    log("Computing phase contribution summary")
    rows = []
    phases = ["M1_related_primary", "middle_primary", "pre_M3_primary", "full_M1_to_M3"]
    sub = counts_df[counts_df["window"].isin(phases)].copy()
    for version_name in sub["version"].unique():
        for threshold in MAG_THRESHOLDS:
            part = sub[(sub["version"] == version_name) & (sub["magnitude_threshold"] == threshold)]
            full_count = float(part.loc[part["window"] == "full_M1_to_M3", "event_count"].iloc[0]) if (part["window"] == "full_M1_to_M3").any() else np.nan
            m1_count = float(part.loc[part["window"] == "M1_related_primary", "event_count"].iloc[0]) if (part["window"] == "M1_related_primary").any() else np.nan
            middle_count = float(part.loc[part["window"] == "middle_primary", "event_count"].iloc[0]) if (part["window"] == "middle_primary").any() else np.nan
            prem3_count = float(part.loc[part["window"] == "pre_M3_primary", "event_count"].iloc[0]) if (part["window"] == "pre_M3_primary").any() else np.nan
            rows.append(
                {
                    "version": version_name,
                    "magnitude_threshold": threshold,
                    "threshold_label": format_threshold_label(threshold),
                    "full_M1_to_M3_count": full_count,
                    "M1_related_count": m1_count,
                    "middle_count": middle_count,
                    "pre_M3_count": prem3_count,
                    "M1_related_fraction_of_full": m1_count / full_count if full_count and pd.notna(full_count) else np.nan,
                    "middle_fraction_of_full": middle_count / full_count if full_count and pd.notna(full_count) else np.nan,
                    "pre_M3_fraction_of_full": prem3_count / full_count if full_count and pd.notna(full_count) else np.nan,
                    "middle_plus_pre_M3_fraction_of_full": (middle_count + prem3_count) / full_count if full_count and pd.notna(full_count) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def classify_burst_phase(start: pd.Timestamp, end: pd.Timestamp, refs: Dict[str, Mainshock]) -> str:
    overlaps = []
    for name in ["M1_related_primary", "middle_primary", "pre_M3_primary", "post_M3_14d"]:
        w0 = parse_bound(WINDOW_DEFINITIONS[name][0], refs)
        w1 = parse_bound(WINDOW_DEFINITIONS[name][1], refs)
        overlap = max(pd.Timedelta(0), min(end, w1) - max(start, w0)) / pd.Timedelta(days=1)
        overlaps.append((name, float(overlap)))
    overlaps.sort(key=lambda x: x[1], reverse=True)
    best_name, best_overlap = overlaps[0]
    if best_overlap <= 0:
        return "mixed/ambiguous"
    mapping = {
        "M1_related_primary": "M1-related dominated phase",
        "middle_primary": "intermediate M1-M3 activity",
        "pre_M3_primary": "pre-M3 local activation",
        "post_M3_14d": "post-M3 context",
    }
    return mapping.get(best_name, "mixed/ambiguous")


def detect_bursts(chain_df: pd.DataFrame, refs: Dict[str, Mainshock]) -> pd.DataFrame:
    log("Detecting major bursts")
    local_df = chain_df[chain_df["in_local_union_60km"]].copy().sort_values("origin_time")
    if local_df.empty:
        return pd.DataFrame()
    bursts = []
    for threshold in [3.0, 4.0]:
        threshold_df = local_df[local_df["magnitude"] >= threshold].copy()
        if threshold_df.empty:
            continue
        times = threshold_df["origin_time"].to_numpy(dtype="datetime64[ns]")
        gap_days = np.diff(times) / np.timedelta64(1, "D")
        split_points = np.where(gap_days > 7.0)[0] + 1
        groups = np.split(np.arange(len(threshold_df)), split_points)
        for group_idx, group in enumerate(groups, start=1):
            if len(group) < MIN_BURST_EVENTS[threshold]:
                continue
            sub = threshold_df.iloc[group].copy()
            start = sub["origin_time"].min()
            end = sub["origin_time"].max()
            duration_days = max((end - start) / pd.Timedelta(days=1), 0.0)
            bursts.append(
                {
                    "burst_id": f"T{int(threshold)}_{group_idx:03d}",
                    "threshold": threshold,
                    "threshold_label": format_threshold_label(threshold),
                    "start_time": start,
                    "end_time": end,
                    "duration_days": duration_days,
                    "event_count": int(len(sub)),
                    "largest_magnitude": float(sub["magnitude"].max()),
                    "mean_magnitude": float(sub["magnitude"].mean()),
                    "min_depth_km": float(sub["depth_km"].min()),
                    "max_depth_km": float(sub["depth_km"].max()),
                    "median_depth_km": float(sub["depth_km"].median()),
                    "centroid_latitude": float(sub["latitude"].mean()),
                    "centroid_longitude": float(sub["longitude"].mean()),
                    "along_axis_centroid_km": float(sub["along_axis_km"].mean()),
                    "dominant_spatial_category": str(sub["spatial_category"].mode().iloc[0]),
                    "M2_related_fraction": float(sub["M2_related_100km"].mean()),
                    "nearest_endpoint_mode": str(sub["nearest_endpoint"].mode().iloc[0]),
                    "phase_class": classify_burst_phase(start, end, refs),
                }
            )
    burst_df = pd.DataFrame(bursts)
    if burst_df.empty:
        return burst_df
    burst_df = burst_df.sort_values(["start_time", "threshold"]).reset_index(drop=True)
    return burst_df


def compute_gap_metrics(chain_df: pd.DataFrame, refs: Dict[str, Mainshock]) -> pd.DataFrame:
    log("Computing continuity/gap metrics")
    rows = []
    local_df = chain_df[chain_df["in_local_union_60km"]].copy().sort_values("origin_time")
    for version_name, version_mask in {
        "raw": pd.Series(True, index=local_df.index),
        "m2aware": ~local_df["M2_related_100km"],
    }.items():
        dfv = local_df[version_mask].copy().sort_values("origin_time")
        for threshold in [0.0, 3.0, 4.0, 5.0]:
            sub = dfv[dfv["magnitude"] >= threshold].copy()
            if len(sub) < 2:
                rows.append(
                    {
                        "version": version_name,
                        "magnitude_threshold": threshold,
                        "threshold_label": format_threshold_label(threshold) if threshold > 0 else "all",
                        "n_events": int(len(sub)),
                        "median_gap_days": np.nan,
                        "p90_gap_days": np.nan,
                        "max_gap_days": np.nan,
                        "full_M1_to_M3_max_gap_days": np.nan,
                        "middle_phase_max_gap_days": np.nan,
                    }
                )
                continue
                continue
            gaps = sub["origin_time"].diff().dropna() / pd.Timedelta(days=1)
            full_sub = sub[sub["window__full_M1_to_M3"]]
            middle_sub = sub[sub["window__middle_primary"]]
            full_gaps = full_sub["origin_time"].diff().dropna() / pd.Timedelta(days=1)
            middle_gaps = middle_sub["origin_time"].diff().dropna() / pd.Timedelta(days=1)
            rows.append(
                {
                    "version": version_name,
                    "magnitude_threshold": threshold,
                    "threshold_label": format_threshold_label(threshold) if threshold > 0 else "all",
                    "n_events": int(len(sub)),
                    "median_gap_days": float(gaps.median()),
                    "p90_gap_days": float(gaps.quantile(0.9)),
                    "max_gap_days": float(gaps.max()),
                    "full_M1_to_M3_max_gap_days": float(full_gaps.max()) if not full_gaps.empty else np.nan,
                    "middle_phase_max_gap_days": float(middle_gaps.max()) if not middle_gaps.empty else np.nan,
                }
            )
    return pd.DataFrame(rows)


def fit_time_trend(sub: pd.DataFrame) -> Tuple[float, float, float]:
    if len(sub) < 3:
        return np.nan, np.nan, np.nan
    x = sub["time_since_M1_days"].to_numpy(dtype=float)
    y = sub["along_axis_km"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    corr = np.corrcoef(x, y)[0, 1] if len(sub) > 1 else np.nan
    return float(slope), float(intercept), float(corr)


def summarize_migration(chain_df: pd.DataFrame) -> pd.DataFrame:
    log("Computing migration / endpoint-switching summary")
    rows = []
    phase_names = ["full_M1_to_M3", "M1_related_primary", "middle_primary", "pre_M3_primary"]
    for version_name, version_mask in {
        "raw": pd.Series(True, index=chain_df.index),
        "m2aware": ~chain_df["M2_related_100km"],
    }.items():
        for phase in phase_names:
            sub = chain_df[chain_df["in_local_union_60km"] & version_mask & chain_df[f"window__{phase}"]].copy()
            slope, intercept, corr = fit_time_trend(sub)
            rows.append(
                {
                    "version": version_name,
                    "phase": phase,
                    "n_events": int(len(sub)),
                    "along_axis_mean_km": float(sub["along_axis_km"].mean()) if len(sub) else np.nan,
                    "along_axis_median_km": float(sub["along_axis_km"].median()) if len(sub) else np.nan,
                    "perp_median_km": float(sub["perpendicular_distance_km"].median()) if len(sub) else np.nan,
                    "slope_km_per_day": slope,
                    "time_along_axis_correlation": corr,
                    "fraction_nearest_M1": float((sub["nearest_endpoint"] == "M1").mean()) if len(sub) else np.nan,
                    "fraction_nearest_M3": float((sub["nearest_endpoint"] == "M3").mean()) if len(sub) else np.nan,
                    "fraction_M1_core": float((sub["spatial_category"] == "M1-core").mean()) if len(sub) else np.nan,
                    "fraction_M3_core": float((sub["spatial_category"] == "M3-core").mean()) if len(sub) else np.nan,
                    "fraction_corridor_noncore": float((sub["spatial_category"] == "corridor_noncore").mean()) if len(sub) else np.nan,
                    "fraction_off_corridor_local": float((sub["spatial_category"] == "off-corridor_local").mean()) if len(sub) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def summarize_controls(chain_df: pd.DataFrame) -> pd.DataFrame:
    log("Computing control comparisons")
    rows = []
    baseline_windows = ["pre_M1_baseline_14d", "pre_M1_baseline_7d"]
    compare_windows = ["M1_related_primary", "middle_primary", "pre_M3_primary", "full_M1_to_M3"]
    for version_name, version_mask in {
        "raw": pd.Series(True, index=chain_df.index),
        "m2aware": ~chain_df["M2_related_100km"],
    }.items():
        for baseline in baseline_windows:
            base_mask = chain_df["in_local_union_60km"] & version_mask & chain_df[f"window__{baseline}"]
            base_duration = get_window_duration_days(chain_df, base_mask)
            base_count = int(base_mask.sum())
            base_rate = base_count / base_duration if base_duration > 0 else np.nan
            base_corridor = int((base_mask & chain_df["in_corridor_20km"]).sum())
            base_off = int((base_mask & chain_df["off_corridor_local"]).sum())
            for compare in compare_windows:
                cmp_mask = chain_df["in_local_union_60km"] & version_mask & chain_df[f"window__{compare}"]
                cmp_duration = get_window_duration_days(chain_df, cmp_mask)
                cmp_count = int(cmp_mask.sum())
                cmp_rate = cmp_count / cmp_duration if cmp_duration > 0 else np.nan
                rows.append(
                    {
                        "version": version_name,
                        "baseline_window": baseline,
                        "compare_window": compare,
                        "baseline_event_count": base_count,
                        "compare_event_count": cmp_count,
                        "baseline_rate_per_day": base_rate,
                        "compare_rate_per_day": cmp_rate,
                        "rate_ratio_compare_to_baseline": cmp_rate / base_rate if pd.notna(base_rate) and base_rate > 0 else np.nan,
                        "baseline_corridor_fraction": base_corridor / base_count if base_count > 0 else np.nan,
                        "baseline_off_corridor_fraction": base_off / base_count if base_count > 0 else np.nan,
                        "compare_corridor_fraction": int((cmp_mask & chain_df["in_corridor_20km"]).sum()) / cmp_count if cmp_count > 0 else np.nan,
                        "compare_off_corridor_fraction": int((cmp_mask & chain_df["off_corridor_local"]).sum()) / cmp_count if cmp_count > 0 else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def build_followup_targets(counts_df: pd.DataFrame, composition_df: pd.DataFrame, migration_df: pd.DataFrame, burst_df: pd.DataFrame) -> pd.DataFrame:
    log("Building follow-up target suggestions")
    rows = []
    for version_name in ["raw", "m2aware"]:
        phase_sub = counts_df[(counts_df["version"] == version_name) & (counts_df["magnitude_threshold"] == 4.0)]
        full = phase_sub.loc[phase_sub["window"] == "full_M1_to_M3", "event_count"]
        m1r = phase_sub.loc[phase_sub["window"] == "M1_related_primary", "event_count"]
        prem3 = phase_sub.loc[phase_sub["window"] == "pre_M3_primary", "event_count"]
        middle = phase_sub.loc[phase_sub["window"] == "middle_primary", "event_count"]
        full_count = float(full.iloc[0]) if not full.empty else np.nan
        m1_count = float(m1r.iloc[0]) if not m1r.empty else np.nan
        prem3_count = float(prem3.iloc[0]) if not prem3.empty else np.nan
        middle_count = float(middle.iloc[0]) if not middle.empty else np.nan
        rows.append(
            {
                "version": version_name,
                "followup_topic": "spatial_depth_screening",
                "priority": "high" if (pd.notna(prem3_count) and prem3_count >= 3) or (burst_df["phase_class"].eq("pre-M3 local activation").any() if not burst_df.empty else False) else "medium",
                "reason": "Check whether pre-M3 or multi-burst activity occupies distinct depth bands or endpoint clusters.",
            }
        )
        rows.append(
            {
                "version": version_name,
                "followup_topic": "b_value_completeness",
                "priority": "high" if pd.notna(full_count) and full_count >= 20 else "medium",
                "reason": "Enough local events to test whether phase-specific magnitude-frequency behavior differs from pre-M1 background.",
            }
        )
        mig = migration_df[(migration_df["version"] == version_name) & (migration_df["phase"] == "full_M1_to_M3")]
        mig_flag = False
        if not mig.empty:
            corr = mig["time_along_axis_correlation"].iloc[0]
            mig_flag = pd.notna(corr) and abs(corr) >= 0.35
        rows.append(
            {
                "version": version_name,
                "followup_topic": "burst_wise_migration_screening",
                "priority": "high" if mig_flag and pd.notna(middle_count) and middle_count >= 3 else "medium",
                "reason": "Only warranted if along-axis trends remain after separating M1-related, middle, and pre-M3 windows.",
            }
        )
        rows.append(
            {
                "version": version_name,
                "followup_topic": "mechanism_screening",
                "priority": "medium",
                "reason": "Mechanisms are optional context; use only for burst or endpoint groups with sufficient coverage.",
            }
        )
    return pd.DataFrame(rows)


def build_classification_summary(counts_df: pd.DataFrame, composition_df: pd.DataFrame, migration_df: pd.DataFrame, controls_df: pd.DataFrame, burst_df: pd.DataFrame) -> pd.DataFrame:
    log("Building screening classification summary")
    rows = []
    for version_name in ["raw", "m2aware"]:
        def get_count(window: str, thr: float) -> float:
            sub = counts_df[(counts_df["version"] == version_name) & (counts_df["window"] == window) & (counts_df["magnitude_threshold"] == thr)]
            return float(sub["event_count"].iloc[0]) if not sub.empty else np.nan

        def get_rate_ratio(baseline: str, compare: str) -> float:
            sub = controls_df[(controls_df["version"] == version_name) & (controls_df["baseline_window"] == baseline) & (controls_df["compare_window"] == compare)]
            return float(sub["rate_ratio_compare_to_baseline"].iloc[0]) if not sub.empty else np.nan

        pre_existing = "present" if get_count("pre_M1_baseline_14d", 3.0) > 0 else "weak_or_absent"
        m1_boost = get_rate_ratio("pre_M1_baseline_14d", "M1_related_primary")
        m1_related_state = "strong" if pd.notna(m1_boost) and m1_boost >= 2.0 else ("moderate" if pd.notna(m1_boost) and m1_boost >= 1.2 else "weak")
        middle_ratio = get_rate_ratio("pre_M1_baseline_14d", "middle_primary")
        middle_state = "sustained" if pd.notna(middle_ratio) and middle_ratio >= 1.0 else ("moderate" if pd.notna(middle_ratio) and middle_ratio >= 0.5 else "quiet")
        prem3_ratio = get_rate_ratio("pre_M1_baseline_14d", "pre_M3_primary")
        prem3_state = "clear_local_activation" if pd.notna(prem3_ratio) and prem3_ratio >= 1.0 and get_count("pre_M3_primary", 3.0) >= 3 else ("limited_or_weak" if get_count("pre_M3_primary", 3.0) > 0 else "absent")

        comp_mid = composition_df[(composition_df["version"] == version_name) & (composition_df["window"] == "middle_primary")]
        comp_pre = composition_df[(composition_df["version"] == version_name) & (composition_df["window"] == "pre_M3_primary")]
        corridor_like = False
        endpoint_centered = False
        if not comp_mid.empty:
            corridor_frac = comp_mid["fraction_corridor_noncore"].iloc[0]
            m1_frac = comp_mid["fraction_M1-core"].iloc[0]
            m3_frac = comp_mid["fraction_M3-core"].iloc[0]
            corridor_like = pd.notna(corridor_frac) and corridor_frac >= max(m1_frac, m3_frac, 0.4)
            endpoint_centered = pd.notna(m1_frac) and pd.notna(m3_frac) and (m1_frac + m3_frac) >= 0.6
        sep_bursts = False
        if not burst_df.empty:
            bsub = burst_df.copy()
            if version_name == "m2aware":
                bsub = bsub[bsub["M2_related_fraction"] < 0.5]
            sep_bursts = len(bsub) >= 2

        mig_full = migration_df[(migration_df["version"] == version_name) & (migration_df["phase"] == "full_M1_to_M3")]
        mig_mid = migration_df[(migration_df["version"] == version_name) & (migration_df["phase"] == "middle_primary")]
        mig_pre = migration_df[(migration_df["version"] == version_name) & (migration_df["phase"] == "pre_M3_primary")]
        apparent_migration = False
        endpoint_switching = False
        if not mig_full.empty:
            corr_full = mig_full["time_along_axis_correlation"].iloc[0]
            corr_mid = mig_mid["time_along_axis_correlation"].iloc[0] if not mig_mid.empty else np.nan
            corr_pre = mig_pre["time_along_axis_correlation"].iloc[0] if not mig_pre.empty else np.nan
            apparent_migration = pd.notna(corr_full) and abs(corr_full) >= 0.35 and ((pd.notna(corr_mid) and abs(corr_mid) >= 0.25) or (pd.notna(corr_pre) and abs(corr_pre) >= 0.25))
            endpoint_switching = pd.notna(corr_full) and abs(corr_full) >= 0.2 and not apparent_migration

        raw_full_m3 = get_count("full_M1_to_M3", 3.0) if version_name == "raw" else np.nan
        m2aware_full_m3 = get_count("full_M1_to_M3", 3.0) if version_name == "m2aware" else np.nan
        if version_name == "raw":
            m2_status = "compare_raw_and_m2aware"
        else:
            raw_ref = counts_df[
                (counts_df["version"] == "raw")
                & (counts_df["window"] == "full_M1_to_M3")
                & (counts_df["magnitude_threshold"] == 3.0)
            ]
            raw_ref_count = float(raw_ref["event_count"].iloc[0]) if not raw_ref.empty else np.nan
            this_count = get_count("full_M1_to_M3", 3.0)
            if pd.notna(raw_ref_count) and raw_ref_count > 0 and pd.notna(this_count):
                frac_removed = (raw_ref_count - this_count) / raw_ref_count
                m2_status = "yes" if frac_removed >= 0.1 else "limited"
            else:
                m2_status = "unclear"

        rows.extend(
            [
                {"version": version_name, "classification_item": "pre_existing_local_activity_before_M1", "classification": pre_existing},
                {"version": version_name, "classification_item": "M1_related_swarm_aftershock_dominated", "classification": m1_related_state},
                {"version": version_name, "classification_item": "middle_phase_activity_after_M1_plus_21d", "classification": middle_state},
                {"version": version_name, "classification_item": "separated_bursts", "classification": "yes" if sep_bursts else "no_or_unclear"},
                {"version": version_name, "classification_item": "endpoint_centered_activity", "classification": "yes" if endpoint_centered else "no_or_mixed"},
                {"version": version_name, "classification_item": "corridor_like_activity", "classification": "yes" if corridor_like else "no_or_mixed"},
                {"version": version_name, "classification_item": "pre_M3_local_activation", "classification": prem3_state},
                {"version": version_name, "classification_item": "continuous_activation_chain", "classification": "unlikely" if middle_state == "quiet" and sep_bursts else "possible_or_mixed"},
                {"version": version_name, "classification_item": "apparent_migration", "classification": "yes" if apparent_migration else "not_robust"},
                {"version": version_name, "classification_item": "endpoint_switching_or_mixed_endpoint_sequences", "classification": "yes" if endpoint_switching else "no_or_unclear"},
                {"version": version_name, "classification_item": "broader_regional_or_background_component", "classification": "present" if not endpoint_centered and not corridor_like else "subordinate"},
                {"version": version_name, "classification_item": "M2_affected_or_ambiguous_mixed_behavior", "classification": m2_status},
            ]
        )
    return pd.DataFrame(rows)


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    log(f"Wrote: {path}")


def main() -> None:
    clean_output_dir(OUTPUT_DIR)
    refs = load_mainshocks(MAINSHOCK_PATH)
    catalog_df = load_catalog(CATALOG_PATH)
    log(f"Catalog events loaded: {len(catalog_df)}")
    catalog_df = build_geometry(catalog_df, refs)
    catalog_df = assign_windows(catalog_df, refs)

    chain_df = catalog_df[(catalog_df["in_local_union_60km"]) | (catalog_df["in_corridor_20km"])].copy()
    chain_df = chain_df.sort_values("origin_time").reset_index(drop=True)
    log(f"M1-M3 local/corridor events retained: {len(chain_df)}")

    reference_df = build_reference_table(refs)
    counts_df = summarize_counts_rates(chain_df, refs)
    composition_df = summarize_composition(chain_df, refs)
    raw_vs_m2_df = summarize_raw_vs_m2aware(counts_df, composition_df)
    phase_df = summarize_phase_contributions(counts_df)
    burst_df = detect_bursts(chain_df, refs)
    gap_df = compute_gap_metrics(chain_df, refs)
    migration_df = summarize_migration(chain_df)
    controls_df = summarize_controls(chain_df)
    followup_df = build_followup_targets(counts_df, composition_df, migration_df, burst_df)
    classification_df = build_classification_summary(counts_df, composition_df, migration_df, controls_df, burst_df)

    required_chain_columns = [
        "event_id",
        "origin_time",
        "latitude",
        "longitude",
        "depth_km",
        "magnitude",
        "time_since_M1_days",
        "time_before_M3_days",
        "distance_to_M1_km",
        "distance_to_M2_km",
        "distance_to_M3_km",
        "along_axis_km",
        "perpendicular_distance_km",
        "spatial_category",
        "M2_related_100km",
    ]
    missing_cols = [c for c in required_chain_columns if c not in chain_df.columns]
    if missing_cols:
        raise ValueError(f"Event-chain table missing required columns: {missing_cols}")

    save_dataframe(chain_df, OUTPUT_DIR / "m1_m3_event_chain_table.csv")
    save_dataframe(reference_df, OUTPUT_DIR / "m1_m3_reference_table.csv")
    save_dataframe(counts_df, OUTPUT_DIR / "m1_m3_window_summary_counts_rates.csv")
    save_dataframe(composition_df, OUTPUT_DIR / "m1_m3_window_summary_composition.csv")
    save_dataframe(raw_vs_m2_df, OUTPUT_DIR / "m1_m3_raw_vs_m2aware_summary.csv")
    save_dataframe(phase_df, OUTPUT_DIR / "m1_m3_phase_contribution_summary.csv")
    save_dataframe(burst_df, OUTPUT_DIR / "m1_m3_burst_table.csv")
    save_dataframe(gap_df, OUTPUT_DIR / "m1_m3_gap_continuity_metrics.csv")
    save_dataframe(migration_df, OUTPUT_DIR / "m1_m3_migration_endpoint_switching_summary.csv")
    save_dataframe(controls_df, OUTPUT_DIR / "m1_m3_control_comparison.csv")
    save_dataframe(followup_df, OUTPUT_DIR / "m1_m3_followup_targets.csv")
    save_dataframe(classification_df, OUTPUT_DIR / "m1_m3_classification_summary.csv")

    log("Completed Task 01 M1-M3 event-chain analysis")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
