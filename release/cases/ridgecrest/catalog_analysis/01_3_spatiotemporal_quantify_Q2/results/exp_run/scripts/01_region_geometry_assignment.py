from __future__ import annotations

import json
import math
import shutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.patches import Circle
from pyproj import CRS, Transformer


REQUIRED_CATALOG_COLUMNS = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
REQUIRED_MAINSHOCK_COLUMNS = ["event_time", "latitude", "longitude", "depth_km", "magnitude"]
REQUIRED_EVENT_OUTPUT_COLUMNS = [
    "event_time",
    "latitude",
    "longitude",
    "depth_km",
    "magnitude",
    "x_km",
    "y_km",
    "energy_joule",
    "hours_since_main64",
    "hours_to_main71",
    "is_all_region",
    "Region_A_along_km",
    "Region_A_across_km",
    "in_Region_A",
    "Region_B_along_km",
    "Region_B_across_km",
    "in_Region_B",
    "dist_to_main64_km",
    "dist_to_main71_km",
    "in_Mw64_neighborhood",
    "in_Mw71_neighborhood",
    "in_corridor_overlap",
    "unassigned_to_corridors",
    "display_assignment_class",
]


CATALOG_PATH = Path("<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv")
MAINSHOCK_PATH = Path("<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv")
FAULT_PATH = Path("<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json")
OUTPUT_DIR = Path("<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/01_region_geometry_assignment")

REGION_A = {
    "name": "Region_A",
    "strike_deg": 39.0,
    "start_lon": -117.635877,
    "start_lat": 35.555024,
    "end_lon": -117.463113,
    "end_lat": 35.729199,
    "half_width_km": 4.0,
}
REGION_B = {
    "name": "Region_B",
    "strike_deg": 138.0,
    "start_lon": -117.735813,
    "start_lat": 35.897499,
    "end_lon": -117.362520,
    "end_lat": 35.559488,
    "half_width_km": 4.0,
}
NEIGHBORHOOD_RADIUS_KM = 10.0
DISPLAY_CLASS_ORDER = ["Region A only", "Region B only", "Overlap A&B", "Unassigned"]


@dataclass
class Corridor:
    name: str
    strike_deg: float
    half_width_km: float
    start_lon: float
    start_lat: float
    end_lon: float
    end_lat: float
    start_x_km: float
    start_y_km: float
    end_x_km: float
    end_y_km: float
    length_km: float
    ux: float
    uy: float
    vx: float
    vy: float
    boundary_xy: np.ndarray


def log(message: str) -> None:
    print(message, flush=True)


def reset_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)
    (output_dir / "tables").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)


def build_local_transformer(center_lon: float, center_lat: float) -> tuple[Transformer, CRS]:
    proj4 = f"+proj=aeqd +lat_0={center_lat} +lon_0={center_lon} +datum=WGS84 +units=m +no_defs"
    crs_local = CRS.from_proj4(proj4)
    transformer = Transformer.from_crs("EPSG:4326", crs_local, always_xy=True)
    return transformer, crs_local


def project_lonlat(transformer: Transformer, lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x_m, y_m = transformer.transform(lon, lat)
    return np.asarray(x_m) / 1000.0, np.asarray(y_m) / 1000.0


def make_corridor(defn: dict, transformer: Transformer) -> Corridor:
    sx, sy = project_lonlat(transformer, np.array([defn["start_lon"]]), np.array([defn["start_lat"]]))
    ex, ey = project_lonlat(transformer, np.array([defn["end_lon"]]), np.array([defn["end_lat"]]))
    sx = float(sx[0])
    sy = float(sy[0])
    ex = float(ex[0])
    ey = float(ey[0])
    dx = ex - sx
    dy = ey - sy
    length = float(math.hypot(dx, dy))
    ux = dx / length
    uy = dy / length
    vx = -uy
    vy = ux
    hw = defn["half_width_km"]
    boundary = np.array([
        [sx + vx * hw, sy + vy * hw],
        [ex + vx * hw, ey + vy * hw],
        [ex - vx * hw, ey - vy * hw],
        [sx - vx * hw, sy - vy * hw],
        [sx + vx * hw, sy + vy * hw],
    ])
    return Corridor(
        name=defn["name"],
        strike_deg=defn["strike_deg"],
        half_width_km=hw,
        start_lon=defn["start_lon"],
        start_lat=defn["start_lat"],
        end_lon=defn["end_lon"],
        end_lat=defn["end_lat"],
        start_x_km=sx,
        start_y_km=sy,
        end_x_km=ex,
        end_y_km=ey,
        length_km=length,
        ux=ux,
        uy=uy,
        vx=vx,
        vy=vy,
        boundary_xy=boundary,
    )


def compute_corridor_coordinates(df: pd.DataFrame, corridor: Corridor) -> pd.DataFrame:
    rx = df["x_km"].to_numpy() - corridor.start_x_km
    ry = df["y_km"].to_numpy() - corridor.start_y_km
    along = rx * corridor.ux + ry * corridor.uy
    across = rx * corridor.vx + ry * corridor.vy
    assigned = (along >= 0.0) & (along <= corridor.length_km) & (np.abs(across) <= corridor.half_width_km)
    return pd.DataFrame(
        {
            f"{corridor.name}_along_km": along,
            f"{corridor.name}_across_km": across,
            f"in_{corridor.name}": assigned,
        },
        index=df.index,
    )


def magnitude_to_energy_joule(magnitude: pd.Series) -> pd.Series:
    return np.power(10.0, 1.5 * magnitude.astype(float) + 4.8)


def load_fault_traces() -> list[np.ndarray]:
    with FAULT_PATH.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    traces = []
    for trace in raw:
        arr = np.asarray(trace, dtype=float)
        if arr.ndim == 2 and arr.shape[1] == 2 and arr.shape[0] >= 2:
            traces.append(arr)
    return traces


def require_columns(df: pd.DataFrame, required_columns: list[str], table_name: str) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {table_name}: {missing}")



def validate_mainshock_table(df: pd.DataFrame) -> None:
    require_columns(df, REQUIRED_MAINSHOCK_COLUMNS, "mainshock table")
    if not np.isfinite(df["magnitude"]).all():
        raise ValueError("Mainshock table contains non-finite magnitude values.")



def select_mainshocks(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    mag64 = df.loc[np.isclose(df["magnitude"], 6.4)].sort_values("event_time")
    mag71 = df.loc[np.isclose(df["magnitude"], 7.1)].sort_values("event_time")
    if mag64.empty or mag71.empty:
        raise ValueError("Mainshock table must contain one Mw 6.4 row and one Mw 7.1 row.")
    row64 = mag64.iloc[0]
    row71 = mag71.iloc[0]
    if pd.Timestamp(row64["event_time"]) >= pd.Timestamp(row71["event_time"]):
        raise ValueError("Mw 6.4 event time must precede Mw 7.1 event time.")
    return row64, row71


def save_metadata(output_dir: Path, crs_local: CRS, main64: pd.Series, main71: pd.Series, corridor_a: Corridor, corridor_b: Corridor) -> None:
    meta = {
        "local_crs_wkt": crs_local.to_wkt(),
        "neighborhood_radius_km": NEIGHBORHOOD_RADIUS_KM,
        "region_a": {
            "strike_deg": corridor_a.strike_deg,
            "half_width_km": corridor_a.half_width_km,
            "length_km": corridor_a.length_km,
            "start_lon": corridor_a.start_lon,
            "start_lat": corridor_a.start_lat,
            "end_lon": corridor_a.end_lon,
            "end_lat": corridor_a.end_lat,
        },
        "region_b": {
            "strike_deg": corridor_b.strike_deg,
            "half_width_km": corridor_b.half_width_km,
            "length_km": corridor_b.length_km,
            "start_lon": corridor_b.start_lon,
            "start_lat": corridor_b.start_lat,
            "end_lon": corridor_b.end_lon,
            "end_lat": corridor_b.end_lat,
        },
        "mainshock64": {
            "event_time": str(main64["event_time"]),
            "longitude": float(main64["longitude"]),
            "latitude": float(main64["latitude"]),
            "magnitude": float(main64["magnitude"]),
        },
        "mainshock71": {
            "event_time": str(main71["event_time"]),
            "longitude": float(main71["longitude"]),
            "latitude": float(main71["latitude"]),
            "magnitude": float(main71["magnitude"]),
        },
        "notes": [
            f"Corridor membership is based on finite-segment projection and {corridor_a.half_width_km:g} km half-width.",
            "Mw6.4-neighborhood and Mw7.1-neighborhood are fixed 10 km radius circles in local metric coordinates.",
            "Display figures may use an exclusive assignment class for symbol styling, but boolean masks remain independent.",
        ],
    }
    with (output_dir / "metadata" / "region_geometry_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def setup_map_axes(ax: plt.Axes, title: str, xlabel: str = "Local x (km)", ylabel: str = "Local y (km)") -> None:
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.2)


def plot_assignment_map(df: pd.DataFrame, fault_traces_xy: list[np.ndarray], main64: pd.Series, main71: pd.Series, corridor_a: Corridor, corridor_b: Corridor, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 10))
    for arr in fault_traces_xy:
        ax.plot(arr[:, 0], arr[:, 1], color="0.75", linewidth=0.35, alpha=0.5, zorder=1)

    mask_after64 = df["hours_since_main64"] >= 0.0
    norm = Normalize(vmin=0.0, vmax=max(1.0, float(df.loc[mask_after64, "hours_since_main64"].max()) if mask_after64.any() else 1.0))
    classes = {
        "Region A only": (df["in_Region_A"] & ~df["in_Region_B"], "o", 18),
        "Region B only": (df["in_Region_B"] & ~df["in_Region_A"], "^", 18),
        "Overlap A&B": (df["in_Region_A"] & df["in_Region_B"], "s", 22),
        "Unassigned": (~df["in_Region_A"] & ~df["in_Region_B"], ".", 8),
    }
    scatter_ref = None
    for label in DISPLAY_CLASS_ORDER:
        mask, marker, size = classes[label]
        subset = df.loc[mask]
        if subset.empty:
            continue
        scatter_ref = ax.scatter(
            subset["x_km"],
            subset["y_km"],
            c=np.clip(subset["hours_since_main64"], a_min=0.0, a_max=None),
            cmap="viridis",
            norm=norm,
            s=size,
            marker=marker,
            linewidths=0.15,
            edgecolors="black" if label != "Unassigned" else "none",
            alpha=0.8 if label != "Unassigned" else 0.55,
            label=label,
            zorder=2 if label == "Unassigned" else 3,
        )

    for corridor, color in [(corridor_a, "tab:red"), (corridor_b, "tab:blue")]:
        ax.plot([corridor.start_x_km, corridor.end_x_km], [corridor.start_y_km, corridor.end_y_km], color=color, linewidth=2.2, label=f"{corridor.name} centerline", zorder=4)
        ax.plot(corridor.boundary_xy[:, 0], corridor.boundary_xy[:, 1], color=color, linestyle="--", linewidth=1.5, label=f"{corridor.name} 6 km corridor", zorder=4)

    for series, color, label in [(main64, "gold", "Mw 6.4"), (main71, "orange", "Mw 7.1")]:
        circle = Circle((series["x_km"], series["y_km"]), NEIGHBORHOOD_RADIUS_KM, fill=False, color=color, linewidth=2.0, linestyle=":", zorder=5)
        ax.add_patch(circle)
        ax.scatter(series["x_km"], series["y_km"], marker="*", s=220, color=color, edgecolor="black", linewidth=0.8, zorder=6)
        ax.text(series["x_km"] + 0.7, series["y_km"] + 0.7, label, fontsize=10, weight="bold", zorder=6)

    if scatter_ref is not None:
        cbar = fig.colorbar(scatter_ref, ax=ax, shrink=0.82)
        cbar.set_label("Hours since Mw 6.4 mainshock")
    setup_map_axes(ax, "Fixed-corridor assignment map with faults, centerlines, 6 km corridors, and 10 km neighborhoods")
    ax.legend(loc="best", fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_distance_distributions(df: pd.DataFrame, corridor: Corridor, output_path: Path) -> None:
    mask = df[f"in_{corridor.name}"]
    values = df.loc[mask, f"{corridor.name}_across_km"].to_numpy()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    if values.size > 0:
        bins = np.linspace(-corridor.half_width_km, corridor.half_width_km, 31)
        ax.hist(values, bins=bins, color="0.4", edgecolor="white")
    ax.axvline(-corridor.half_width_km, color="tab:red", linestyle="--", linewidth=1.5, label=f"-{corridor.half_width_km:g} km half-width")
    ax.axvline(corridor.half_width_km, color="tab:red", linestyle="--", linewidth=1.5, label=f"+{corridor.half_width_km:g} km half-width")
    ax.set_title(f"{corridor.name} across-centerline distance distribution")
    ax.set_xlabel("Perpendicular distance to centerline (km)")
    ax.set_ylabel("Assigned event count")
    ax.grid(True, alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_along_distributions(df: pd.DataFrame, corridor: Corridor, output_path: Path) -> None:
    mask = df[f"in_{corridor.name}"]
    values = df.loc[mask, f"{corridor.name}_along_km"].to_numpy()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    if values.size > 0:
        bins = np.linspace(0.0, corridor.length_km, 41)
        ax.hist(values, bins=bins, color="0.35", edgecolor="white")
    ax.axvline(0.0, color="tab:blue", linestyle="--", linewidth=1.5, label="Centerline start")
    ax.axvline(corridor.length_km, color="tab:blue", linestyle="--", linewidth=1.5, label="Centerline end")
    ax.set_title(f"{corridor.name} along-strike coordinate distribution")
    ax.set_xlabel("Along-strike distance from centerline start (km)")
    ax.set_ylabel("Assigned event count")
    ax.grid(True, alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_unassigned_map(df: pd.DataFrame, fault_traces_xy: list[np.ndarray], corridor_a: Corridor, corridor_b: Corridor, main64: pd.Series, main71: pd.Series, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 10))
    for arr in fault_traces_xy:
        ax.plot(arr[:, 0], arr[:, 1], color="0.8", linewidth=0.35, alpha=0.6, zorder=1)
    unassigned = df.loc[~df["in_Region_A"] & ~df["in_Region_B"]]
    assigned = df.loc[df["in_Region_A"] | df["in_Region_B"]]
    if not assigned.empty:
        ax.scatter(assigned["x_km"], assigned["y_km"], s=8, color="lightgrey", alpha=0.35, label="Assigned to A and/or B", zorder=2)
    if not unassigned.empty:
        ax.scatter(unassigned["x_km"], unassigned["y_km"], s=10, color="black", alpha=0.65, label="Unassigned to corridors", zorder=3)
    for corridor, color in [(corridor_a, "tab:red"), (corridor_b, "tab:blue")]:
        ax.plot([corridor.start_x_km, corridor.end_x_km], [corridor.start_y_km, corridor.end_y_km], color=color, linewidth=2.0, zorder=4)
        ax.plot(corridor.boundary_xy[:, 0], corridor.boundary_xy[:, 1], color=color, linestyle="--", linewidth=1.4, zorder=4)
    for series, color, label in [(main64, "gold", "Mw 6.4"), (main71, "orange", "Mw 7.1")]:
        ax.scatter(series["x_km"], series["y_km"], marker="*", s=210, color=color, edgecolor="black", linewidth=0.8, zorder=5)
        ax.text(series["x_km"] + 0.7, series["y_km"] + 0.7, label, fontsize=10, weight="bold", zorder=5)
    setup_map_axes(ax, "Unassigned-event diagnostic map")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def validate_event_output_schema(df: pd.DataFrame) -> None:
    require_columns(df, REQUIRED_EVENT_OUTPUT_COLUMNS, "event assignment output table")



def build_assignment_summary(df: pd.DataFrame, corridor_a: Corridor, corridor_b: Corridor) -> pd.DataFrame:
    rows = []
    total = len(df)
    overlap_count = int((df["in_Region_A"] & df["in_Region_B"]).sum())
    unassigned_frac = float((~df["in_Region_A"] & ~df["in_Region_B"]).mean())
    for corridor in [corridor_a, corridor_b]:
        mask = df[f"in_{corridor.name}"]
        subset = df.loc[mask]
        across_abs = subset[f"{corridor.name}_across_km"].abs()
        along_vals = subset[f"{corridor.name}_along_km"]
        rows.append(
            {
                "region": corridor.name,
                "assigned_event_count": int(mask.sum()),
                "assigned_fraction": float(mask.mean()),
                "corridor_overlap_count": overlap_count,
                "corridor_overlap_fraction": overlap_count / total if total > 0 else np.nan,
                "unassigned_corridor_fraction": unassigned_frac,
                "median_abs_across_km": float(across_abs.median()) if len(across_abs) else np.nan,
                "p95_abs_across_km": float(across_abs.quantile(0.95)) if len(across_abs) else np.nan,
                "along_min_km": float(along_vals.min()) if len(along_vals) else np.nan,
                "along_max_km": float(along_vals.max()) if len(along_vals) else np.nan,
                "centerline_length_km": corridor.length_km,
                "half_width_km": corridor.half_width_km,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    try:
        log(f"Preparing output directory: {OUTPUT_DIR}")
        reset_output_dir(OUTPUT_DIR)

        log(f"Loading catalog: {CATALOG_PATH}")
        catalog = pd.read_csv(CATALOG_PATH, parse_dates=["event_time"])
        require_columns(catalog, REQUIRED_CATALOG_COLUMNS, "catalog")
        log(f"Loaded {len(catalog):,} catalog events")

        log(f"Loading mainshocks: {MAINSHOCK_PATH}")
        mainshocks = pd.read_csv(MAINSHOCK_PATH, parse_dates=["event_time"])
        validate_mainshock_table(mainshocks)
        main64, main71 = select_mainshocks(mainshocks)
        log(f"Mw 6.4 event time: {main64['event_time']}")
        log(f"Mw 7.1 event time: {main71['event_time']}")

        catalog = catalog.sort_values("event_time").reset_index(drop=True)
        catalog = catalog.loc[catalog["event_time"] <= main71["event_time"]].copy()
        if catalog.empty:
            raise ValueError("Catalog is empty after truncation to the pre-Mw7.1 time window.")
        log(f"Catalog truncated to pre-Mw7.1 window: {len(catalog):,} events")

        center_lon = float(np.r_[catalog["longitude"].to_numpy(), mainshocks["longitude"].to_numpy()].mean())
        center_lat = float(np.r_[catalog["latitude"].to_numpy(), mainshocks["latitude"].to_numpy()].mean())
        transformer, crs_local = build_local_transformer(center_lon, center_lat)
        log("Built local azimuthal equidistant projection")

        x_km, y_km = project_lonlat(transformer, catalog["longitude"].to_numpy(), catalog["latitude"].to_numpy())
        catalog["x_km"] = x_km
        catalog["y_km"] = y_km
        catalog["energy_joule"] = magnitude_to_energy_joule(catalog["magnitude"])
        catalog["hours_since_main64"] = (catalog["event_time"] - main64["event_time"]).dt.total_seconds() / 3600.0
        catalog["hours_to_main71"] = (main71["event_time"] - catalog["event_time"]).dt.total_seconds() / 3600.0
        catalog["is_all_region"] = True

        main_xy_x, main_xy_y = project_lonlat(transformer, mainshocks["longitude"].to_numpy(), mainshocks["latitude"].to_numpy())
        mainshocks = mainshocks.copy()
        mainshocks["x_km"] = main_xy_x
        mainshocks["y_km"] = main_xy_y
        main64 = mainshocks.loc[np.isclose(mainshocks["magnitude"], 6.4)].sort_values("event_time").iloc[0]
        main71 = mainshocks.loc[np.isclose(mainshocks["magnitude"], 7.1)].sort_values("event_time").iloc[0]

        corridor_a = make_corridor(REGION_A, transformer)
        corridor_b = make_corridor(REGION_B, transformer)
        log(f"Region A centerline length: {corridor_a.length_km:.2f} km")
        log(f"Region B centerline length: {corridor_b.length_km:.2f} km")

        catalog = pd.concat([catalog, compute_corridor_coordinates(catalog, corridor_a), compute_corridor_coordinates(catalog, corridor_b)], axis=1)
        validate_event_output_schema(catalog.assign(
            dist_to_main64_km=np.nan,
            dist_to_main71_km=np.nan,
            in_Mw64_neighborhood=False,
            in_Mw71_neighborhood=False,
            in_corridor_overlap=False,
            unassigned_to_corridors=False,
            display_assignment_class="",
        ))

        catalog["dist_to_main64_km"] = np.hypot(catalog["x_km"] - float(main64["x_km"]), catalog["y_km"] - float(main64["y_km"]))
        catalog["dist_to_main71_km"] = np.hypot(catalog["x_km"] - float(main71["x_km"]), catalog["y_km"] - float(main71["y_km"]))
        catalog["in_Mw64_neighborhood"] = catalog["dist_to_main64_km"] <= NEIGHBORHOOD_RADIUS_KM
        catalog["in_Mw71_neighborhood"] = catalog["dist_to_main71_km"] <= NEIGHBORHOOD_RADIUS_KM
        catalog["in_corridor_overlap"] = catalog["in_Region_A"] & catalog["in_Region_B"]
        catalog["unassigned_to_corridors"] = ~catalog["in_Region_A"] & ~catalog["in_Region_B"]

        display_class = np.full(len(catalog), "Unassigned", dtype=object)
        display_class[catalog["in_Region_A"].to_numpy() & ~catalog["in_Region_B"].to_numpy()] = "Region A only"
        display_class[catalog["in_Region_B"].to_numpy() & ~catalog["in_Region_A"].to_numpy()] = "Region B only"
        display_class[catalog["in_Region_A"].to_numpy() & catalog["in_Region_B"].to_numpy()] = "Overlap A&B"
        catalog["display_assignment_class"] = display_class
        validate_event_output_schema(catalog)

        log(f"Loading faults: {FAULT_PATH}")
        fault_traces_ll = load_fault_traces()
        fault_traces_xy = []
        for trace in fault_traces_ll:
            tx, ty = project_lonlat(transformer, trace[:, 0], trace[:, 1])
            fault_traces_xy.append(np.column_stack([tx, ty]))
        log(f"Projected {len(fault_traces_xy):,} fault traces")

        event_table_path = OUTPUT_DIR / "tables" / "event_region_assignments.csv"
        summary_path = OUTPUT_DIR / "tables" / "region_assignment_summary.csv"
        catalog.to_csv(event_table_path, index=False)
        summary_df = build_assignment_summary(catalog, corridor_a, corridor_b)
        summary_df.to_csv(summary_path, index=False)
        log(f"Saved event-level enriched table: {event_table_path}")
        log(f"Saved assignment summary: {summary_path}")

        save_metadata(OUTPUT_DIR, crs_local, main64, main71, corridor_a, corridor_b)

        fig_dir = OUTPUT_DIR / "figures"
        plot_assignment_map(catalog, fault_traces_xy, main64, main71, corridor_a, corridor_b, fig_dir / "fixed_corridor_assignment_map.png")
        plot_distance_distributions(catalog, corridor_a, fig_dir / "region_a_across_centerline_distribution.png")
        plot_distance_distributions(catalog, corridor_b, fig_dir / "region_b_across_centerline_distribution.png")
        plot_along_distributions(catalog, corridor_a, fig_dir / "region_a_along_strike_distribution.png")
        plot_along_distributions(catalog, corridor_b, fig_dir / "region_b_along_strike_distribution.png")
        plot_unassigned_map(catalog, fault_traces_xy, corridor_a, corridor_b, main64, main71, fig_dir / "unassigned_event_diagnostic_map.png")
        log(f"Saved figures to: {fig_dir}")

        log("Assignment counts:")
        log(summary_df.to_string(index=False))
        if int(catalog["in_Region_A"].sum()) == 0 or int(catalog["in_Region_B"].sum()) == 0:
            raise RuntimeError("One or both fixed corridors received zero assigned events, which violates task expectations.")

        log("Task 01_region_geometry_assignment completed successfully.")
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
