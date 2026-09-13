from __future__ import annotations

import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_DIR = Path("<CASE_ROOT>/data")
CATALOG_DIR = DATA_DIR / "catalog"
SCRIPT_PATH = Path("<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/scripts/02_aomori_bootstrap_controls.py")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/02_aomori_bootstrap_controls")
PRIMARY_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_4_bg_rate_correction/exp_run/outputs/01_aomori_background_rate_analysis")
PRIMARY_TABLES_DIR = PRIMARY_OUTPUT_DIR / "tables"
PRIMARY_FIGURES_DIR = PRIMARY_OUTPUT_DIR / "figures"

LONG_TERM_PATH = CATALOG_DIR / "Snet_catalog_20200101_20260522_filter.csv"
ACTIVE_REQUESTED_PATH = DATA_DIR / "Snet_catalog_20251001_20260501_filter.csv"
ACTIVE_CANDIDATE_PATHS = [
    ACTIVE_REQUESTED_PATH,
    CATALOG_DIR / "Snet_catalog_20251001_20260501_filter.csv",
    CATALOG_DIR / "Snet_catalog_relocate_250930_260501.csv",
]
MAINSHOCK_PATH = CATALOG_DIR / "main_earthquake.csv"

ACTIVE_START = pd.Timestamp("2025-10-01T00:00:00Z")
ACTIVE_END = pd.Timestamp("2026-05-01T23:59:59Z")
LONG_TERM_START = pd.Timestamp("2020-01-01T00:00:00Z")
LONG_TERM_END = pd.Timestamp("2026-05-22T23:59:59Z")

MAIN_RADIUS_KM = 35.0
RESAMPLE_N = 4000
SHIFTED_WINDOW_STEP_DAYS = 7
BOOTSTRAP_SEED = 20260524
MAX_WORKERS = max(1, min(8, (os.cpu_count() or 1) - 1))
COUNT_FLOOR_FOR_RATIO = 0.5

THRESHOLDS = [3.0, 4.0, 5.0]
WINDOWS = {
    "7D": pd.Timedelta(days=7),
    "14D": pd.Timedelta(days=14),
    "30D": pd.Timedelta(days=30),
    "active_period": ACTIVE_END - ACTIVE_START,
}
DEPTH_BINS = [(0.0, 30.0), (30.0, 60.0), (60.0, np.inf)]
TARGET_REGIONS = ["common_region", "m1_m3_local_union", "m2_near_field", "m2_outer_band", "control_region"]


@dataclass(frozen=True)
class Region:
    name: str
    kind: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    inner_radius_km: Optional[float] = None
    outer_radius_km: Optional[float] = None
    exclude_other_main_circles: bool = False
    notes: str = ""


def log(message: str) -> None:
    print(message, flush=True)


def ensure_output_dirs() -> Dict[str, Path]:
    subdirs = {
        "root": OUTPUT_DIR,
        "tables": OUTPUT_DIR / "tables",
        "figures": OUTPUT_DIR / "figures",
        "diagnostics": OUTPUT_DIR / "diagnostics",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for sub in subdirs.values():
        sub.mkdir(parents=True, exist_ok=True)
    for file_path in OUTPUT_DIR.glob("*.txt"):
        file_path.unlink()
    for sub_name in ["tables", "figures", "diagnostics"]:
        for file_path in (OUTPUT_DIR / sub_name).glob("*"):
            if file_path.is_file():
                file_path.unlink()
    return subdirs


def save_table(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    log(f"Saved table: {path}")


def resolve_active_catalog_path() -> Tuple[Path, str]:
    for idx, candidate in enumerate(ACTIVE_CANDIDATE_PATHS):
        if candidate.exists():
            if idx == 0:
                note = f"Active-period catalog found at requested path: {candidate}"
            elif candidate.name == "Snet_catalog_20251001_20260501_filter.csv":
                note = f"Active-period catalog found under catalog directory: {candidate}"
            else:
                note = f"Active-period analysis catalog path resolved to: {candidate}"
            return candidate, note
    raise FileNotFoundError(
        "No active-period catalog found. Checked: " + ", ".join(str(path) for path in ACTIVE_CANDIDATE_PATHS)
    )


def parse_catalog(path: Path, name: str) -> pd.DataFrame:
    log(f"Reading catalog: {name} <- {path}")
    df = pd.read_csv(path)
    expected = ["datetime", "lat", "lon", "dep", "mag"]
    if list(df.columns) != expected:
        raise ValueError(f"Unexpected schema for {name}: {df.columns.tolist()}")
    out = pd.DataFrame(
        {
            "datetime": pd.to_datetime(df["datetime"], utc=True, errors="coerce"),
            "lat": pd.to_numeric(df["lat"], errors="coerce"),
            "lon": pd.to_numeric(df["lon"], errors="coerce"),
            "dep": pd.to_numeric(df["dep"], errors="coerce"),
            "mag": pd.to_numeric(df["mag"], errors="coerce"),
        }
    ).dropna()
    out = out.sort_values("datetime").reset_index(drop=True)
    out["catalog"] = name
    return out


def parse_mainshocks(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    for col in ["lat", "lon", "dep", "mag"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df[["datetime", "lat", "lon", "dep", "mag"]].isna().any().any():
        raise ValueError("Mainshock table contains invalid values")
    return df


def load_regions(path: Path) -> Dict[str, Region]:
    df = pd.read_csv(path)
    regions: Dict[str, Region] = {}
    for _, row in df.iterrows():
        regions[row["name"]] = Region(
            name=row["name"],
            kind=row["kind"],
            min_lat=float(row["min_lat"]),
            max_lat=float(row["max_lat"]),
            min_lon=float(row["min_lon"]),
            max_lon=float(row["max_lon"]),
            center_lat=None if pd.isna(row["center_lat"]) else float(row["center_lat"]),
            center_lon=None if pd.isna(row["center_lon"]) else float(row["center_lon"]),
            inner_radius_km=None if pd.isna(row["inner_radius_km"]) else float(row["inner_radius_km"]),
            outer_radius_km=None if pd.isna(row["outer_radius_km"]) else float(row["outer_radius_km"]),
            exclude_other_main_circles=bool(row["exclude_other_main_circles"]),
            notes=str(row["notes"]),
        )
    return regions


def haversine_km(lat1, lon1, lat2, lon2):
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * 6371.0 * np.arcsin(np.sqrt(a))


def region_mask(df: pd.DataFrame, region: Region, mainshock_df: Optional[pd.DataFrame] = None) -> pd.Series:
    base = (
        (df["lat"] >= region.min_lat)
        & (df["lat"] <= region.max_lat)
        & (df["lon"] >= region.min_lon)
        & (df["lon"] <= region.max_lon)
    )
    if region.kind == "bbox":
        return base
    if region.kind in {"circle", "ring"}:
        dist = haversine_km(df["lat"].values, df["lon"].values, region.center_lat, region.center_lon)
        if region.kind == "circle":
            mask = base & (dist <= float(region.outer_radius_km))
        else:
            mask = base & (dist > float(region.inner_radius_km)) & (dist <= float(region.outer_radius_km))
        if region.exclude_other_main_circles and mainshock_df is not None:
            for _, row in mainshock_df.iterrows():
                if abs(row["lat"] - region.center_lat) < 1e-9 and abs(row["lon"] - region.center_lon) < 1e-9:
                    continue
                other_dist = haversine_km(df["lat"].values, df["lon"].values, row["lat"], row["lon"])
                mask &= other_dist > MAIN_RADIUS_KM
        return pd.Series(mask, index=df.index)
    raise ValueError(f"Unknown region kind: {region.kind}")


def get_region_mask(df: pd.DataFrame, region_name: str, regions: Dict[str, Region], mainshocks: pd.DataFrame) -> pd.Series:
    if region_name == "m1_m3_local_union":
        return region_mask(df, regions["m1_local"], mainshocks) | region_mask(df, regions["m3_local"], mainshocks)
    if region_name == "control_region":
        base = region_mask(df, regions["common_region"], mainshocks)
        excluded = (
            region_mask(df, regions["m1_local"], mainshocks)
            | region_mask(df, regions["m2_local"], mainshocks)
            | region_mask(df, regions["m3_local"], mainshocks)
            | region_mask(df, regions["m2_outer_band"], mainshocks)
        )
        return base & (~excluded)
    return region_mask(df, regions[region_name], mainshocks)


def depth_label(low: float, high: float) -> str:
    if np.isinf(high):
        return f">={int(low)} km"
    return f"{int(low)}-{int(high)} km"


def build_region_depth_event_times(
    long_df: pd.DataFrame,
    active_df: pd.DataFrame,
    regions: Dict[str, Region],
    mainshocks: pd.DataFrame,
) -> Dict[Tuple[str, str], Dict[str, np.ndarray]]:
    payload: Dict[Tuple[str, str], Dict[str, np.ndarray]] = {}
    log("Building region/depth event-time payloads")
    for region_name in TARGET_REGIONS:
        long_region = long_df.loc[get_region_mask(long_df, region_name, regions, mainshocks)].copy()
        active_region = active_df.loc[get_region_mask(active_df, region_name, regions, mainshocks)].copy()
        for low, high in DEPTH_BINS:
            label = depth_label(low, high)
            long_depth = long_region[(long_region["dep"] >= low) & (long_region["dep"] < high)].copy()
            active_depth = active_region[(active_region["dep"] >= low) & (active_region["dep"] < high)].copy()
            payload[(region_name, label)] = {
                "long_times": long_depth["datetime"].values.astype("datetime64[ns]"),
                "long_mag": long_depth["mag"].to_numpy(dtype=float),
                "active_times": active_depth["datetime"].values.astype("datetime64[ns]"),
                "active_mag": active_depth["mag"].to_numpy(dtype=float),
            }
    return payload


def sliding_window_counts_from_arrays(
    event_times: np.ndarray,
    event_mags: np.ndarray,
    threshold: float,
    window: pd.Timedelta,
    start: pd.Timestamp,
    end: pd.Timestamp,
    exclude_intervals: Optional[List[Tuple[np.datetime64, np.datetime64]]] = None,
    step_days: int = 1,
) -> np.ndarray:
    if event_times.size == 0:
        return np.array([], dtype=int)
    mask = event_mags >= threshold
    times = np.sort(event_times[mask])
    starts = pd.date_range(start=start, end=end - window, freq=f"{step_days}D", tz="UTC")
    if len(starts) == 0:
        return np.array([], dtype=int)
    start_vals = starts.tz_convert(None).values.astype("datetime64[ns]")
    valid = np.ones(len(start_vals), dtype=bool)
    if exclude_intervals:
        end_vals = (starts + window).values.astype("datetime64[ns]")
        for exc_start, exc_end in exclude_intervals:
            overlap = (start_vals <= exc_end) & (end_vals >= exc_start)
            valid &= ~overlap
    start_vals = start_vals[valid]
    if start_vals.size == 0:
        return np.array([], dtype=int)
    end_vals = start_vals + np.timedelta64(int(window / pd.Timedelta(seconds=1)), "s")
    left = np.searchsorted(times, start_vals, side="left")
    right = np.searchsorted(times, end_vals, side="right")
    return (right - left).astype(int)


def bootstrap_poisson_ratio(background_counts: np.ndarray, observed_count: int, rng: np.random.Generator, n: int) -> Dict[str, float]:
    background_counts = np.asarray(background_counts, dtype=float)
    if background_counts.size == 0:
        return {
            "expected_mean": np.nan,
            "expected_median": np.nan,
            "expected_ci_low": np.nan,
            "expected_ci_high": np.nan,
            "ratio_mean": np.nan,
            "ratio_ci_low": np.nan,
            "ratio_ci_high": np.nan,
            "excess_mean": np.nan,
            "excess_ci_low": np.nan,
            "excess_ci_high": np.nan,
            "percentile": np.nan,
            "exceedance_fraction": np.nan,
        }
    sampled = rng.choice(background_counts, size=n, replace=True)
    ratios = observed_count / np.maximum(sampled, COUNT_FLOOR_FOR_RATIO)
    excess = observed_count - sampled
    percentile = 100.0 * float(np.mean(background_counts <= observed_count))
    exceedance_fraction = float(np.mean(background_counts >= observed_count))
    return {
        "expected_mean": float(np.mean(sampled)),
        "expected_median": float(np.median(sampled)),
        "expected_ci_low": float(np.percentile(sampled, 2.5)),
        "expected_ci_high": float(np.percentile(sampled, 97.5)),
        "ratio_mean": float(np.mean(ratios)),
        "ratio_ci_low": float(np.percentile(ratios, 2.5)),
        "ratio_ci_high": float(np.percentile(ratios, 97.5)),
        "excess_mean": float(np.mean(excess)),
        "excess_ci_low": float(np.percentile(excess, 2.5)),
        "excess_ci_high": float(np.percentile(excess, 97.5)),
        "percentile": percentile,
        "exceedance_fraction": exceedance_fraction,
    }


def summarize_shifted_active_windows(
    event_times: np.ndarray,
    event_mags: np.ndarray,
    threshold: float,
    window: pd.Timedelta,
) -> Dict[str, float]:
    starts = pd.date_range(start=ACTIVE_START, end=ACTIVE_END - window, freq=f"{SHIFTED_WINDOW_STEP_DAYS}D", tz="UTC")
    if len(starts) == 0:
        observed = int(np.sum(event_mags >= threshold))
        return {
            "n_shifted_windows": 1,
            "active_shifted_mean": float(observed),
            "active_shifted_median": float(observed),
            "active_shifted_max": float(observed),
            "active_shifted_percentile": 100.0,
        }
    mask = event_mags >= threshold
    times = np.sort(event_times[mask])
    start_vals = starts.values.astype("datetime64[ns]")
    end_vals = start_vals + np.timedelta64(int(window / pd.Timedelta(seconds=1)), "s")
    left = np.searchsorted(times, start_vals, side="left")
    right = np.searchsorted(times, end_vals, side="right")
    counts = (right - left).astype(int)
    observed = int(np.sum(mask)) if window == WINDOWS["active_period"] else int(counts[0])
    percentile = 100.0 * float(np.mean(counts <= observed)) if counts.size else np.nan
    return {
        "n_shifted_windows": int(counts.size),
        "active_shifted_mean": float(np.mean(counts)) if counts.size else np.nan,
        "active_shifted_median": float(np.median(counts)) if counts.size else np.nan,
        "active_shifted_max": float(np.max(counts)) if counts.size else np.nan,
        "active_shifted_percentile": percentile,
    }


def worker_task(args: Tuple[str, str, float, str, int, Dict[str, np.ndarray]]) -> Dict[str, object]:
    region_name, depth_bin, threshold, window_name, seed, arrays = args
    rng = np.random.default_rng(seed)
    window = WINDOWS[window_name]
    long_times = arrays["long_times"]
    long_mag = arrays["long_mag"]
    active_times = arrays["active_times"]
    active_mag = arrays["active_mag"]

    if window_name == "active_period":
        observed_count = int(np.sum(active_mag >= threshold))
    else:
        observed_array = sliding_window_counts_from_arrays(
            active_times,
            active_mag,
            threshold,
            window,
            ACTIVE_START,
            ACTIVE_START + window,
            None,
            1,
        )
        observed_count = int(observed_array[0]) if observed_array.size else 0

    random_counts = sliding_window_counts_from_arrays(
        long_times,
        long_mag,
        threshold,
        window,
        LONG_TERM_START,
        LONG_TERM_END,
        exclude_intervals=None,
        step_days=1,
    )
    outside_counts = sliding_window_counts_from_arrays(
        long_times,
        long_mag,
        threshold,
        window,
        LONG_TERM_START,
        LONG_TERM_END,
        exclude_intervals=[(np.datetime64(ACTIVE_START.tz_convert(None)), np.datetime64(ACTIVE_END.tz_convert(None)))],
        step_days=1,
    )

    random_stats = bootstrap_poisson_ratio(random_counts, observed_count, rng, RESAMPLE_N)
    outside_stats = bootstrap_poisson_ratio(outside_counts, observed_count, rng, RESAMPLE_N)
    shifted_stats = summarize_shifted_active_windows(active_times, active_mag, threshold, window)

    result = {
        "region": region_name,
        "depth_bin": depth_bin,
        "threshold": threshold,
        "window_name": window_name,
        "observed_count": observed_count,
        "n_random_windows": int(random_counts.size),
        "n_outside_windows": int(outside_counts.size),
        **{f"random_{k}": v for k, v in random_stats.items()},
        **{f"outside_{k}": v for k, v in outside_stats.items()},
        **shifted_stats,
    }
    required_cols = {
        "region",
        "depth_bin",
        "threshold",
        "window_name",
        "observed_count",
        "n_random_windows",
        "n_outside_windows",
        "random_expected_mean",
        "random_ratio_mean",
        "random_percentile",
        "outside_expected_mean",
        "outside_ratio_mean",
        "outside_percentile",
        "active_shifted_mean",
        "active_shifted_percentile",
    }
    missing = sorted(required_cols - set(result))
    if missing:
        raise ValueError(f"Worker result missing required fields: {missing}")
    return result


def plot_control_heatmap(df: pd.DataFrame, value_col: str, title: str, fig_path: Path) -> None:
    required_cols = {"region", "depth_bin", "threshold", value_col}
    missing = sorted(required_cols - set(df.columns))
    if missing:
        raise ValueError(f"Heatmap input missing required columns: {missing}")
    subset = df.copy()
    if subset.empty:
        return
    subset["row"] = subset["region"].astype(str) + " | " + subset["depth_bin"].astype(str)
    pivot = subset.pivot_table(index="row", columns="threshold", values=value_col, aggfunc="first")
    fig, ax = plt.subplots(figsize=(10, max(5, 0.35 * len(pivot))))
    im = ax.imshow(pivot.values, aspect="auto", cmap="magma")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels([f"M≥{x:g}" for x in pivot.columns])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.set_title(title)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            ax.text(j, i, "nan" if pd.isna(val) else f"{val:.2f}", ha="center", va="center", color="white", fontsize=7)
    fig.colorbar(im, ax=ax, label=value_col)
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200)
    plt.close(fig)


def plot_random_vs_outside(df: pd.DataFrame, fig_path: Path) -> None:
    required_cols = {"region", "depth_bin", "threshold", "random_ratio_mean", "outside_ratio_mean", "random_percentile", "outside_percentile"}
    missing = sorted(required_cols - set(df.columns))
    if missing:
        raise ValueError(f"Scatter input missing required columns: {missing}")
    subset = df.copy()
    subset = subset[np.isfinite(subset["random_ratio_mean"]) & np.isfinite(subset["outside_ratio_mean"])].copy()
    if subset.empty:
        return

    subset["label"] = subset["region"].astype(str) + " | " + subset["depth_bin"].astype(str) + " | M≥" + subset["threshold"].map(lambda x: f"{x:g}")
    subset["annotation_score"] = (
        subset["random_ratio_mean"].fillna(0.0)
        + subset["outside_ratio_mean"].fillna(0.0)
        + 0.02 * subset["random_percentile"].fillna(0.0)
        + 0.02 * subset["outside_percentile"].fillna(0.0)
    )
    annotate_df = subset.sort_values("annotation_score", ascending=False).head(12).copy()

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(subset["random_ratio_mean"], subset["outside_ratio_mean"], s=40, alpha=0.75, color="tab:blue", edgecolors="none")
    line_max = float(np.nanmax([subset["random_ratio_mean"].max(), subset["outside_ratio_mean"].max(), 1.0]))
    ax.plot([0, line_max], [0, line_max], "k--", lw=1)

    x_span = max(line_max, 1.0)
    y_span = x_span
    x_offset = 0.012 * x_span
    y_offset = 0.012 * y_span
    used_positions = []
    for _, row in annotate_df.iterrows():
        x = float(row["random_ratio_mean"])
        y = float(row["outside_ratio_mean"])
        if not (np.isfinite(x) and np.isfinite(y)):
            continue
        dx = x_offset
        dy = y_offset
        for prev_x, prev_y in used_positions:
            if abs((x + dx) - prev_x) < 0.05 * x_span and abs((y + dy) - prev_y) < 0.05 * y_span:
                dy += 0.03 * y_span
        text_x = x + dx
        text_y = y + dy
        used_positions.append((text_x, text_y))
        ax.annotate(
            row["label"],
            xy=(x, y),
            xytext=(text_x, text_y),
            textcoords="data",
            fontsize=7,
            ha="left",
            va="bottom",
            arrowprops={"arrowstyle": "-", "lw": 0.5, "color": "0.4", "alpha": 0.8},
            bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "0.7", "alpha": 0.9},
        )

    ax.set_xlabel("Bootstrap ratio mean vs all long-term random windows")
    ax.set_ylabel("Bootstrap ratio mean vs long-term windows outside active dates")
    ax.set_title("Control comparison for active-period windows")
    note = f"Annotated top {len(annotate_df)} outliers by control-score; dense core points left unlabeled for readability"
    ax.text(0.02, 0.98, note, transform=ax.transAxes, ha="left", va="top", fontsize=8,
            bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "0.8", "alpha": 0.9})
    fig.tight_layout()
    fig.savefig(fig_path, dpi=200)
    plt.close(fig)


def build_merged_evidence(primary_evidence: pd.DataFrame, bootstrap_df: pd.DataFrame) -> pd.DataFrame:
    required_primary_cols = {"region", "depth_bin", "threshold", "observed_count", "expected_count", "obs_exp_ratio"}
    missing_primary = sorted(required_primary_cols - set(primary_evidence.columns))
    if missing_primary:
        raise ValueError(f"Primary evidence table missing required columns: {missing_primary}")
    required_bootstrap_cols = {
        "region",
        "depth_bin",
        "threshold",
        "window_name",
        "random_expected_mean",
        "random_percentile",
        "random_exceedance_fraction",
        "random_ratio_mean",
        "random_ratio_ci_low",
        "random_ratio_ci_high",
        "outside_expected_mean",
        "outside_percentile",
        "outside_exceedance_fraction",
        "outside_ratio_mean",
        "outside_ratio_ci_low",
        "outside_ratio_ci_high",
        "active_shifted_mean",
        "active_shifted_percentile",
        "n_random_windows",
        "n_outside_windows",
    }
    missing_bootstrap = sorted(required_bootstrap_cols - set(bootstrap_df.columns))
    if missing_bootstrap:
        raise ValueError(f"Bootstrap control table missing required columns: {missing_bootstrap}")
    active_subset = bootstrap_df[bootstrap_df["window_name"] == "active_period"].copy()
    merged = primary_evidence.merge(
        active_subset[[
            "region",
            "depth_bin",
            "threshold",
            "random_expected_mean",
            "random_percentile",
            "random_exceedance_fraction",
            "random_ratio_mean",
            "random_ratio_ci_low",
            "random_ratio_ci_high",
            "outside_expected_mean",
            "outside_percentile",
            "outside_exceedance_fraction",
            "outside_ratio_mean",
            "outside_ratio_ci_low",
            "outside_ratio_ci_high",
            "active_shifted_mean",
            "active_shifted_percentile",
            "n_random_windows",
            "n_outside_windows",
        ]],
        on=["region", "depth_bin", "threshold"],
        how="left",
        validate="one_to_one",
    )

    def classify(row: pd.Series) -> str:
        ratio = row.get("random_ratio_mean")
        pct = row.get("random_percentile")
        outside_pct = row.get("outside_percentile")
        if pd.isna(ratio) or pd.isna(pct):
            return "insufficient_control_data"
        if ratio >= 3.0 and pct >= 97.5 and (pd.isna(outside_pct) or outside_pct >= 95.0):
            return "very_strong"
        if ratio >= 2.0 and pct >= 95.0:
            return "strong"
        if ratio >= 1.5 and pct >= 90.0:
            return "moderate"
        if ratio >= 1.2 and pct >= 75.0:
            return "weak"
        return "not_unusual"

    merged["control_support_level"] = merged.apply(classify, axis=1)
    return merged


def build_report(merged_df: pd.DataFrame, diagnostics_df: pd.DataFrame, path: Path) -> None:
    active = merged_df.copy()
    active = active.sort_values(["control_support_level", "random_ratio_mean", "random_percentile"], ascending=[True, False, False])
    top = active.sort_values(["random_ratio_mean", "random_percentile"], ascending=[False, False]).head(12)
    lines = [
        "Aomori bootstrap/control resampling summary",
        f"Primary outputs source: {PRIMARY_OUTPUT_DIR}",
        f"Long-term catalog: {LONG_TERM_PATH}",
        f"Active-period window: {ACTIVE_START.isoformat()} to {ACTIVE_END.isoformat()}",
        f"Bootstrap/random resamples per combination: {RESAMPLE_N}",
        f"Parallel workers requested: {MAX_WORKERS}",
        "",
        "Top active-period anomalies after control resampling:",
    ]
    for _, row in top.iterrows():
        lines.append(
            f"- {row['region']} | {row['depth_bin']} | M>={row['threshold']:g}: obs/exp(primary)={row['obs_exp_ratio']:.2f}, "
            f"random_ratio_mean={row['random_ratio_mean']:.2f}, random_percentile={row['random_percentile']:.1f}, "
            f"outside_percentile={row['outside_percentile']:.1f}, support={row['control_support_level']}"
        )
    lines.append("")
    lines.append("Execution diagnostics:")
    for _, row in diagnostics_df.iterrows():
        lines.append(f"- {row['item']}: {row['value']}")
    path.write_text("\n".join(lines), encoding="utf-8")
    log(f"Saved report: {path}")


def main() -> None:
    dirs = ensure_output_dirs()
    log(f"Output root: {dirs['root']}")
    required_primary = [
        PRIMARY_TABLES_DIR / "region_definitions.csv",
        PRIMARY_TABLES_DIR / "background_rate_evidence_matrix.csv",
        PRIMARY_TABLES_DIR / "threshold_reliability.csv",
    ]
    missing = [str(p) for p in required_primary if not p.exists()]
    if missing:
        raise FileNotFoundError("Validated primary outputs missing: " + ", ".join(missing))

    active_path, active_note = resolve_active_catalog_path()
    long_df = parse_catalog(LONG_TERM_PATH, "long_term_raw")
    active_df = parse_catalog(active_path, "active_relocated")
    mainshocks = parse_mainshocks(MAINSHOCK_PATH)
    regions = load_regions(PRIMARY_TABLES_DIR / "region_definitions.csv")
    primary_evidence = pd.read_csv(PRIMARY_TABLES_DIR / "background_rate_evidence_matrix.csv")
    threshold_reliability = pd.read_csv(PRIMARY_TABLES_DIR / "threshold_reliability.csv")
    reliable_thresholds = set(threshold_reliability.loc[threshold_reliability["reliable_for_long_term_comparison"], "threshold"].astype(float).tolist())
    selected_thresholds = [thr for thr in THRESHOLDS if thr in reliable_thresholds]
    if not selected_thresholds:
        raise ValueError("No reliable thresholds available for bootstrap controls")
    log(active_note)
    log(f"Selected thresholds for bootstrap controls: {selected_thresholds}")

    long_df = long_df[(long_df["datetime"] >= LONG_TERM_START) & (long_df["datetime"] <= LONG_TERM_END)].copy()
    active_df = active_df[(active_df["datetime"] >= ACTIVE_START) & (active_df["datetime"] <= ACTIVE_END)].copy()
    long_df = long_df.loc[get_region_mask(long_df, "common_region", regions, mainshocks)].copy()
    active_df = active_df.loc[get_region_mask(active_df, "common_region", regions, mainshocks)].copy()

    payload = build_region_depth_event_times(long_df, active_df, regions, mainshocks)

    tasks: List[Tuple[str, str, float, str, int, Dict[str, np.ndarray]]] = []
    seed_seq = np.random.SeedSequence(BOOTSTRAP_SEED)
    combo_count = len(TARGET_REGIONS) * len(DEPTH_BINS) * len(selected_thresholds) * len(WINDOWS)
    child_seeds = seed_seq.spawn(combo_count)
    idx = 0
    for region_name in TARGET_REGIONS:
        for low, high in DEPTH_BINS:
            depth_bin = depth_label(low, high)
            arrays = payload[(region_name, depth_bin)]
            for threshold in selected_thresholds:
                for window_name in WINDOWS:
                    tasks.append((region_name, depth_bin, threshold, window_name, int(child_seeds[idx].generate_state(1)[0]), arrays))
                    idx += 1

    log(f"Launching {len(tasks)} bootstrap/control jobs with up to {MAX_WORKERS} workers")
    results: List[Dict[str, object]] = []
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(worker_task, task): task[:4] for task in tasks}
        completed = 0
        for future in as_completed(futures):
            completed += 1
            region_name, depth_bin, threshold, window_name = futures[future]
            log(f"Completed {completed}/{len(futures)}: region={region_name}, depth={depth_bin}, threshold={threshold}, window={window_name}")
            results.append(future.result())

    bootstrap_df = pd.DataFrame(results)
    required_bootstrap_df_cols = {
        "region",
        "depth_bin",
        "threshold",
        "window_name",
        "observed_count",
        "random_expected_mean",
        "random_percentile",
        "outside_expected_mean",
        "outside_percentile",
    }
    missing_bootstrap_df_cols = sorted(required_bootstrap_df_cols - set(bootstrap_df.columns))
    if missing_bootstrap_df_cols:
        raise ValueError(f"Assembled bootstrap results missing required columns: {missing_bootstrap_df_cols}")
    bootstrap_df = bootstrap_df.sort_values(["region", "depth_bin", "threshold", "window_name"]).reset_index(drop=True)
    save_table(bootstrap_df, dirs["tables"] / "bootstrap_random_window_controls.csv")

    merged_df = build_merged_evidence(primary_evidence, bootstrap_df)
    save_table(merged_df, dirs["tables"] / "background_rate_evidence_matrix_with_controls.csv")

    diagnostics = pd.DataFrame(
        [
            {"item": "script_path", "value": str(SCRIPT_PATH)},
            {"item": "primary_output_dir", "value": str(PRIMARY_OUTPUT_DIR)},
            {"item": "active_catalog_path", "value": str(active_path)},
            {"item": "selected_thresholds", "value": ",".join(str(x) for x in selected_thresholds)},
            {"item": "resample_n", "value": str(RESAMPLE_N)},
            {"item": "max_workers", "value": str(MAX_WORKERS)},
            {"item": "task_count", "value": str(len(tasks))},
            {"item": "long_term_common_events", "value": str(len(long_df))},
            {"item": "active_common_events", "value": str(len(active_df))},
        ]
    )
    save_table(diagnostics, dirs["diagnostics"] / "run_diagnostics.csv")

    plot_control_heatmap(
        merged_df,
        value_col="random_ratio_mean",
        title="Bootstrap control mean ratio for active-period windows",
        fig_path=dirs["figures"] / "01_bootstrap_control_ratio_heatmap.png",
    )
    plot_control_heatmap(
        merged_df,
        value_col="random_percentile",
        title="Long-term percentile of active-period windows after bootstrap controls",
        fig_path=dirs["figures"] / "02_bootstrap_control_percentile_heatmap.png",
    )
    plot_random_vs_outside(
        merged_df,
        fig_path=dirs["figures"] / "03_random_vs_outside_control_scatter.png",
    )

    build_report(merged_df, diagnostics, OUTPUT_DIR / "summary_report.txt")
    log("Bootstrap/control workflow completed successfully")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
