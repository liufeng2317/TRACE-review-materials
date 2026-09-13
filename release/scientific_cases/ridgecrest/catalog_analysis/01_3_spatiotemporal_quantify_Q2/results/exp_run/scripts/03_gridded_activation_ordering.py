from __future__ import annotations

import json
import math
import os
import shutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from matplotlib.patches import Circle
from pyproj import CRS, Transformer

CATALOG_ASSIGNMENTS_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/01_region_geometry_assignment/tables/event_region_assignments.csv"
)
GEOMETRY_METADATA_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/01_region_geometry_assignment/metadata/region_geometry_metadata.json"
)
FAULT_PATH = Path(
    "<REPO_ROOT>/examples/ridgecrest/data/faults/ridgecrest_surface_faults.json"
)
OUTPUT_DIR = Path(
    "<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_3_trigger_spatiotemporal_quantify_Q2-v1/exp_run/outputs/03_gridded_activation_ordering"
)

CELL_SIZE_KM = 0.5
HALF_HOUR_HOURS = 0.5
ONE_HOUR_HOURS = 1.0
MAX_CORES = 64
ALONG_STRIKE_BIN_KM = 0.5
ZERO_CELL_COLOR = "#d9d9d9"
HEATMAP_ZERO_COLOR = "#efefef"
CMAP_NAME = "viridis"


@dataclass
class Corridor:
    name: str
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


@dataclass
class Mainshock:
    name: str
    event_time: pd.Timestamp
    longitude: float
    latitude: float
    x_km: float
    y_km: float
    magnitude: float


@dataclass
class CircleDomain:
    name: str
    center_x_km: float
    center_y_km: float
    radius_km: float
    mask_column: str


def log(message: str) -> None:
    print(message, flush=True)


def reset_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "figures").mkdir(exist_ok=True)
    (output_dir / "tables").mkdir(exist_ok=True)
    (output_dir / "metadata").mkdir(exist_ok=True)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_transformers(local_crs_wkt: str) -> tuple[Transformer, Transformer]:
    local_crs = CRS.from_wkt(local_crs_wkt)
    fwd = Transformer.from_crs("EPSG:4326", local_crs, always_xy=True)
    inv = Transformer.from_crs(local_crs, "EPSG:4326", always_xy=True)
    return fwd, inv


def project_lonlat(transformer: Transformer, lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x_m, y_m = transformer.transform(lon, lat)
    return np.asarray(x_m) / 1000.0, np.asarray(y_m) / 1000.0


def inverse_project(transformer: Transformer, x_km: np.ndarray, y_km: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon, lat = transformer.transform(np.asarray(x_km) * 1000.0, np.asarray(y_km) * 1000.0)
    return np.asarray(lon), np.asarray(lat)


def make_corridor(defn: dict, transformer: Transformer, name: str) -> Corridor:
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
    hw = float(defn["half_width_km"])
    boundary = np.array([
        [sx + vx * hw, sy + vy * hw],
        [ex + vx * hw, ey + vy * hw],
        [ex - vx * hw, ey - vy * hw],
        [sx - vx * hw, sy - vy * hw],
        [sx + vx * hw, sy + vy * hw],
    ])
    return Corridor(
        name=name,
        half_width_km=hw,
        start_lon=float(defn["start_lon"]),
        start_lat=float(defn["start_lat"]),
        end_lon=float(defn["end_lon"]),
        end_lat=float(defn["end_lat"]),
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


def enrich_mainshocks(metadata: dict, transformer: Transformer) -> tuple[Mainshock, Mainshock]:
    rows = []
    for key, name in [("mainshock64", "Mw6.4"), ("mainshock71", "Mw7.1")]:
        d = metadata[key]
        x, y = project_lonlat(transformer, np.array([d["longitude"]]), np.array([d["latitude"]]))
        rows.append(
            Mainshock(
                name=name,
                event_time=pd.Timestamp(d["event_time"]),
                longitude=float(d["longitude"]),
                latitude=float(d["latitude"]),
                x_km=float(x[0]),
                y_km=float(y[0]),
                magnitude=float(d["magnitude"]),
            )
        )
    return rows[0], rows[1]


def build_circle_domains(main64: Mainshock, main71: Mainshock, radius_km: float) -> list[CircleDomain]:
    return [
        CircleDomain(
            name="Mw6.4_neighborhood",
            center_x_km=main64.x_km,
            center_y_km=main64.y_km,
            radius_km=radius_km,
            mask_column="in_Mw64_neighborhood",
        ),
        CircleDomain(
            name="Mw7.1_neighborhood",
            center_x_km=main71.x_km,
            center_y_km=main71.y_km,
            radius_km=radius_km,
            mask_column="in_Mw71_neighborhood",
        ),
    ]


def build_time_edges(max_hours: float, step_hours: float) -> np.ndarray:
    nbins = int(math.ceil(max_hours / step_hours))
    return np.linspace(0.0, nbins * step_hours, nbins + 1)


def first_nonzero_bin_center(counts: np.ndarray, edges: np.ndarray) -> float:
    idx = np.flatnonzero(counts > 0)
    if idx.size == 0:
        return np.nan
    return float((edges[idx[0]] + edges[idx[0] + 1]) / 2.0)


def peak_rate_time(counts: np.ndarray, edges: np.ndarray) -> float:
    if counts.size == 0 or np.all(counts == 0):
        return np.nan
    idx = int(np.argmax(counts))
    return float((edges[idx] + edges[idx + 1]) / 2.0)


def generate_corridor_grid(corridor: Corridor, cell_size_km: float) -> pd.DataFrame:
    along_centers = np.arange(cell_size_km / 2.0, corridor.length_km, cell_size_km)
    across_centers = np.arange(-corridor.half_width_km + cell_size_km / 2.0, corridor.half_width_km, cell_size_km)
    along_grid, across_grid = np.meshgrid(along_centers, across_centers, indexing="xy")
    along_flat = along_grid.ravel()
    across_flat = across_grid.ravel()
    x = corridor.start_x_km + along_flat * corridor.ux + across_flat * corridor.vx
    y = corridor.start_y_km + along_flat * corridor.uy + across_flat * corridor.vy
    return pd.DataFrame(
        {
            "cell_id": np.arange(along_flat.size, dtype=int),
            "along_km": along_flat,
            "across_km": across_flat,
            "x_km": x,
            "y_km": y,
        }
    )


def generate_circle_grid(domain: CircleDomain, cell_size_km: float) -> pd.DataFrame:
    x_centers = np.arange(domain.center_x_km - domain.radius_km + cell_size_km / 2.0, domain.center_x_km + domain.radius_km, cell_size_km)
    y_centers = np.arange(domain.center_y_km - domain.radius_km + cell_size_km / 2.0, domain.center_y_km + domain.radius_km, cell_size_km)
    xg, yg = np.meshgrid(x_centers, y_centers, indexing="xy")
    x_flat = xg.ravel()
    y_flat = yg.ravel()
    dist = np.hypot(x_flat - domain.center_x_km, y_flat - domain.center_y_km)
    mask = dist <= domain.radius_km + 1e-9
    return pd.DataFrame(
        {
            "cell_id": np.arange(mask.sum(), dtype=int),
            "x_km": x_flat[mask],
            "y_km": y_flat[mask],
        }
    )


def assign_corridor_cell_indices(events: pd.DataFrame, cell_size_km: float, corridor: Corridor) -> tuple[np.ndarray, np.ndarray]:
    along = events[f"{corridor.name}_along_km"].to_numpy()
    across = events[f"{corridor.name}_across_km"].to_numpy()
    along_idx = np.floor(along / cell_size_km).astype(int)
    across_idx = np.floor((across + corridor.half_width_km) / cell_size_km).astype(int)
    return along_idx, across_idx


def assign_circle_cell_indices(events: pd.DataFrame, cell_size_km: float, domain: CircleDomain) -> tuple[np.ndarray, np.ndarray]:
    x = events["x_km"].to_numpy()
    y = events["y_km"].to_numpy()
    x_idx = np.floor((x - (domain.center_x_km - domain.radius_km)) / cell_size_km).astype(int)
    y_idx = np.floor((y - (domain.center_y_km - domain.radius_km)) / cell_size_km).astype(int)
    return x_idx, y_idx


def summarize_group(
    cell_id: int,
    idx: np.ndarray,
    event_hours: np.ndarray,
    event_energy: np.ndarray,
    edges_30m: np.ndarray,
    edges_1h: np.ndarray,
) -> dict:
    if idx.size == 0:
        return {
            "cell_id": cell_id,
            "event_count": 0,
            "cumulative_energy": 0.0,
            "first_activation_hours": np.nan,
            "peak_rate_time_30m_hours": np.nan,
            "peak_rate_time_1h_hours": np.nan,
            "first_nonzero_bin_30m_hours": np.nan,
            "first_nonzero_bin_1h_hours": np.nan,
            "counts_30m": np.zeros(edges_30m.size - 1, dtype=int),
            "counts_1h": np.zeros(edges_1h.size - 1, dtype=int),
        }
    hours = event_hours[idx]
    energy = event_energy[idx]
    counts_30m, _ = np.histogram(hours, bins=edges_30m)
    counts_1h, _ = np.histogram(hours, bins=edges_1h)
    return {
        "cell_id": cell_id,
        "event_count": int(idx.size),
        "cumulative_energy": float(np.sum(energy)),
        "first_activation_hours": float(np.nanmin(hours)),
        "peak_rate_time_30m_hours": peak_rate_time(counts_30m, edges_30m),
        "peak_rate_time_1h_hours": peak_rate_time(counts_1h, edges_1h),
        "first_nonzero_bin_30m_hours": first_nonzero_bin_center(counts_30m, edges_30m),
        "first_nonzero_bin_1h_hours": first_nonzero_bin_center(counts_1h, edges_1h),
        "counts_30m": counts_30m,
        "counts_1h": counts_1h,
    }


def parallel_group_summaries(
    group_map: dict[int, np.ndarray],
    event_hours: np.ndarray,
    event_energy: np.ndarray,
    edges_30m: np.ndarray,
    edges_1h: np.ndarray,
    n_jobs: int,
) -> list[dict]:
    ordered = sorted(group_map.items(), key=lambda kv: kv[0])
    return Parallel(n_jobs=n_jobs, prefer="processes", verbose=10)(
        delayed(summarize_group)(cell_id, idx, event_hours, event_energy, edges_30m, edges_1h)
        for cell_id, idx in ordered
    )


def build_group_map(cell_ids: np.ndarray, total_cells: int) -> dict[int, np.ndarray]:
    mapping = {cid: np.empty(0, dtype=int) for cid in range(total_cells)}
    if cell_ids.size == 0:
        return mapping
    order = np.argsort(cell_ids)
    sorted_ids = cell_ids[order]
    unique_ids, starts = np.unique(sorted_ids, return_index=True)
    starts = np.append(starts, sorted_ids.size)
    for uid, s0, s1 in zip(unique_ids, starts[:-1], starts[1:]):
        mapping[int(uid)] = order[s0:s1]
    return mapping


def corridor_cell_table(
    region_name: str,
    events: pd.DataFrame,
    corridor: Corridor,
    main64: Mainshock,
    main71: Mainshock,
    inv_transformer: Transformer,
    max_hours: float,
    n_jobs: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    log(f"Building cell table for {region_name}...")
    grid = generate_corridor_grid(corridor, CELL_SIZE_KM)
    if grid.empty:
        raise ValueError(f"{region_name} corridor grid is empty.")
    along_count = int(grid["along_km"].nunique())
    across_count = int(grid["across_km"].nunique())

    region_events = events.loc[events[f"in_{corridor.name}"] & (events["hours_since_main64"] >= 0.0)].copy()
    log(f"{region_name}: post-Mw6.4 assigned events = {len(region_events)}")

    edges_30m = build_time_edges(max_hours, HALF_HOUR_HOURS)
    edges_1h = build_time_edges(max_hours, ONE_HOUR_HOURS)

    if region_events.empty:
        raise ValueError(f"{region_name} contains no post-Mw6.4 events inside fixed corridor.")

    along_idx, across_idx = assign_corridor_cell_indices(region_events, CELL_SIZE_KM, corridor)
    valid = (
        (along_idx >= 0)
        & (along_idx < along_count)
        & (across_idx >= 0)
        & (across_idx < across_count)
    )
    region_events = region_events.loc[valid].copy()
    along_idx = along_idx[valid]
    across_idx = across_idx[valid]
    region_events["cell_id"] = across_idx * along_count + along_idx

    group_map = build_group_map(region_events["cell_id"].to_numpy(dtype=int), len(grid))
    summaries = parallel_group_summaries(
        group_map=group_map,
        event_hours=region_events["hours_since_main64"].to_numpy(float),
        event_energy=region_events["energy_joule"].to_numpy(float),
        edges_30m=edges_30m,
        edges_1h=edges_1h,
        n_jobs=n_jobs,
    )
    summary_df = pd.DataFrame(summaries).sort_values("cell_id").reset_index(drop=True)
    if summary_df.empty:
        raise ValueError(f"{region_name} summary table is empty.")
    cell_df = grid.merge(summary_df.drop(columns=["counts_30m", "counts_1h"]), on="cell_id", how="left")
    required_cell_cols = {
        "cell_id",
        "along_km",
        "across_km",
        "x_km",
        "y_km",
        "event_count",
        "cumulative_energy",
        "first_activation_hours",
        "peak_rate_time_30m_hours",
        "peak_rate_time_1h_hours",
        "first_nonzero_bin_30m_hours",
        "first_nonzero_bin_1h_hours",
    }
    missing = required_cell_cols.difference(cell_df.columns)
    if missing:
        raise ValueError(f"{region_name} cell table missing required columns after merge: {sorted(missing)}")
    lon, lat = inverse_project(inv_transformer, cell_df["x_km"].to_numpy(), cell_df["y_km"].to_numpy())
    cell_df["longitude"] = lon
    cell_df["latitude"] = lat
    cell_df["distance_to_Mw6.4_km"] = np.hypot(cell_df["x_km"] - main64.x_km, cell_df["y_km"] - main64.y_km)
    cell_df["distance_to_Mw7.1_km"] = np.hypot(cell_df["x_km"] - main71.x_km, cell_df["y_km"] - main71.y_km)
    cell_df.insert(0, "region", region_name)

    grid_lookup = grid.set_index("cell_id")[["along_km", "across_km"]]
    heatmap_rows = []
    for s in summaries:
        cid = int(s["cell_id"])
        meta = grid_lookup.loc[cid]
        counts_30m = s["counts_30m"]
        counts_1h = s["counts_1h"]
        for i in range(counts_30m.size):
            heatmap_rows.append(
                {
                    "region": region_name,
                    "cell_id": cid,
                    "along_km": meta["along_km"],
                    "across_km": meta["across_km"],
                    "resolution": "30min",
                    "bin_start_hours": edges_30m[i],
                    "bin_end_hours": edges_30m[i + 1],
                    "event_count": int(counts_30m[i]),
                    "rate_per_hour": float(counts_30m[i] / HALF_HOUR_HOURS),
                }
            )
        for i in range(counts_1h.size):
            heatmap_rows.append(
                {
                    "region": region_name,
                    "cell_id": cid,
                    "along_km": meta["along_km"],
                    "across_km": meta["across_km"],
                    "resolution": "1h",
                    "bin_start_hours": edges_1h[i],
                    "bin_end_hours": edges_1h[i + 1],
                    "event_count": int(counts_1h[i]),
                    "rate_per_hour": float(counts_1h[i] / ONE_HOUR_HOURS),
                }
            )
    heatmap_df = pd.DataFrame(heatmap_rows)

    region_events["along_bin_center_km"] = (np.floor(region_events[f"{corridor.name}_along_km"] / ALONG_STRIKE_BIN_KM) * ALONG_STRIKE_BIN_KM) + ALONG_STRIKE_BIN_KM / 2.0
    grouped = region_events.groupby("along_bin_center_km", sort=True)
    along_rows = []
    for center, g in grouped:
        counts_30m, _ = np.histogram(g["hours_since_main64"].to_numpy(), bins=edges_30m)
        along_rows.append(
            {
                "region": region_name,
                "along_bin_center_km": float(center),
                "event_count": int(len(g)),
                "first_activation_hours": float(g["hours_since_main64"].min()),
                "peak_rate_time_30m_hours": peak_rate_time(counts_30m, edges_30m),
                "cumulative_energy": float(g["energy_joule"].sum()),
            }
        )
    along_df = pd.DataFrame(along_rows)
    if along_df.empty:
        raise ValueError(f"{region_name} along-strike summary is empty.")
    expected_along_cols = {
        "region",
        "along_bin_center_km",
        "event_count",
        "first_activation_hours",
        "peak_rate_time_30m_hours",
        "cumulative_energy",
    }
    missing = expected_along_cols.difference(along_df.columns)
    if missing:
        raise ValueError(f"{region_name} along-strike summary missing columns: {sorted(missing)}")
    return cell_df, heatmap_df, along_df


def neighborhood_cell_table(
    domain: CircleDomain,
    events: pd.DataFrame,
    main64: Mainshock,
    main71: Mainshock,
    inv_transformer: Transformer,
    max_hours: float,
    n_jobs: int,
) -> pd.DataFrame:
    log(f"Building neighborhood cell table for {domain.name}...")
    grid = generate_circle_grid(domain, CELL_SIZE_KM)
    if grid.empty:
        raise ValueError(f"{domain.name} neighborhood grid is empty.")
    domain_events = events.loc[events[domain.mask_column] & (events["hours_since_main64"] >= 0.0)].copy()
    if domain_events.empty:
        raise ValueError(f"{domain.name} contains no post-Mw6.4 events.")

    edges_30m = build_time_edges(max_hours, HALF_HOUR_HOURS)
    edges_1h = build_time_edges(max_hours, ONE_HOUR_HOURS)

    x_idx, y_idx = assign_circle_cell_indices(domain_events, CELL_SIZE_KM, domain)
    x_count = int(round((2.0 * domain.radius_km) / CELL_SIZE_KM))
    y_count = x_count
    valid = (x_idx >= 0) & (x_idx < x_count) & (y_idx >= 0) & (y_idx < y_count)
    domain_events = domain_events.loc[valid].copy()
    x_idx = x_idx[valid]
    y_idx = y_idx[valid]

    center_lookup = {
        (int(np.floor((x - (domain.center_x_km - domain.radius_km)) / CELL_SIZE_KM)), int(np.floor((y - (domain.center_y_km - domain.radius_km)) / CELL_SIZE_KM))): cid
        for cid, x, y in grid[["cell_id", "x_km", "y_km"]].itertuples(index=False)
    }
    cell_ids = np.array([center_lookup.get((ix, iy), -1) for ix, iy in zip(x_idx, y_idx)], dtype=int)
    valid_ids = cell_ids >= 0
    domain_events = domain_events.loc[valid_ids].copy()
    cell_ids = cell_ids[valid_ids]
    domain_events["cell_id"] = cell_ids

    group_map = build_group_map(domain_events["cell_id"].to_numpy(dtype=int), len(grid))
    summaries = parallel_group_summaries(
        group_map=group_map,
        event_hours=domain_events["hours_since_main64"].to_numpy(float),
        event_energy=domain_events["energy_joule"].to_numpy(float),
        edges_30m=edges_30m,
        edges_1h=edges_1h,
        n_jobs=n_jobs,
    )
    summary_df = pd.DataFrame(summaries).sort_values("cell_id").reset_index(drop=True)
    if summary_df.empty:
        raise ValueError(f"{domain.name} neighborhood summary table is empty.")
    cell_df = grid.merge(summary_df.drop(columns=["counts_30m", "counts_1h"]), on="cell_id", how="left")
    required_cell_cols = {
        "cell_id",
        "x_km",
        "y_km",
        "event_count",
        "cumulative_energy",
        "first_activation_hours",
        "peak_rate_time_30m_hours",
        "peak_rate_time_1h_hours",
        "first_nonzero_bin_30m_hours",
        "first_nonzero_bin_1h_hours",
    }
    missing = required_cell_cols.difference(cell_df.columns)
    if missing:
        raise ValueError(f"{domain.name} neighborhood cell table missing required columns after merge: {sorted(missing)}")
    lon, lat = inverse_project(inv_transformer, cell_df["x_km"].to_numpy(), cell_df["y_km"].to_numpy())
    cell_df["longitude"] = lon
    cell_df["latitude"] = lat
    cell_df["distance_to_Mw6.4_km"] = np.hypot(cell_df["x_km"] - main64.x_km, cell_df["y_km"] - main64.y_km)
    cell_df["distance_to_Mw7.1_km"] = np.hypot(cell_df["x_km"] - main71.x_km, cell_df["y_km"] - main71.y_km)
    cell_df.insert(0, "domain", domain.name)
    return cell_df


def truncate_cmap(name: str, minval: float = 0.0, maxval: float = 1.0, n: int = 256):
    cmap = plt.get_cmap(name)
    return mcolors.LinearSegmentedColormap.from_list(
        f"trunc_{name}", cmap(np.linspace(minval, maxval, n))
    )


def plot_corridor_cumulative_maps(
    cell_tables: dict[str, pd.DataFrame],
    corridors: dict[str, Corridor],
    main64: Mainshock,
    main71: Mainshock,
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    cmap = truncate_cmap(CMAP_NAME, 0.08, 1.0)
    for ax, region_name in zip(axes, ["Region_A", "Region_B"]):
        df = cell_tables[region_name]
        corridor = corridors[region_name]
        positive = df["event_count"] > 0
        vmax = max(float(df.loc[positive, "event_count"].max()) if positive.any() else 1.0, 1.0)
        ax.scatter(df.loc[~positive, "x_km"], df.loc[~positive, "y_km"], s=24, c=ZERO_CELL_COLOR, marker="s", linewidths=0)
        sc = ax.scatter(
            df.loc[positive, "x_km"],
            df.loc[positive, "y_km"],
            s=24,
            c=df.loc[positive, "event_count"],
            cmap=cmap,
            vmin=1,
            vmax=vmax,
            marker="s",
            linewidths=0,
        )
        ax.plot(corridor.boundary_xy[:, 0], corridor.boundary_xy[:, 1], color="black", lw=1.2)
        ax.plot([corridor.start_x_km, corridor.end_x_km], [corridor.start_y_km, corridor.end_y_km], color="black", lw=1.2, ls="--")
        ax.scatter([main64.x_km], [main64.y_km], color="red", marker="*", s=130, label="Mw 6.4")
        ax.scatter([main71.x_km], [main71.y_km], color="orange", marker="*", s=130, label="Mw 7.1")
        ax.set_title(f"{region_name.replace('_', ' ')} cumulative count")
        ax.set_xlabel("Local x (km)")
        ax.set_ylabel("Local y (km)")
        ax.set_aspect("equal", adjustable="box")
        cbar = fig.colorbar(sc, ax=ax, shrink=0.82)
        cbar.set_label("Cumulative event count")
    axes[0].legend(loc="upper left")
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_corridor_first_activation_maps(
    cell_tables: dict[str, pd.DataFrame],
    corridors: dict[str, Corridor],
    main64: Mainshock,
    main71: Mainshock,
    max_hours: float,
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    cmap = truncate_cmap(CMAP_NAME, 0.12, 1.0)
    for ax, region_name in zip(axes, ["Region_A", "Region_B"]):
        df = cell_tables[region_name]
        corridor = corridors[region_name]
        inactive = df["event_count"] == 0
        active = df["event_count"] > 0
        ax.scatter(df.loc[inactive, "x_km"], df.loc[inactive, "y_km"], s=24, c=ZERO_CELL_COLOR, marker="s", linewidths=0)
        sc = ax.scatter(
            df.loc[active, "x_km"],
            df.loc[active, "y_km"],
            s=24,
            c=df.loc[active, "first_activation_hours"],
            cmap=cmap,
            vmin=0.0,
            vmax=max_hours,
            marker="s",
            linewidths=0,
        )
        ax.plot(corridor.boundary_xy[:, 0], corridor.boundary_xy[:, 1], color="black", lw=1.2)
        ax.plot([corridor.start_x_km, corridor.end_x_km], [corridor.start_y_km, corridor.end_y_km], color="black", lw=1.0, ls="--")
        ax.scatter([main64.x_km], [main64.y_km], color="red", marker="*", s=130)
        ax.scatter([main71.x_km], [main71.y_km], color="orange", marker="*", s=130)
        ax.text(main64.x_km + 0.4, main64.y_km + 0.4, "Mw 6.4", color="red", fontsize=9)
        ax.text(main71.x_km + 0.4, main71.y_km + 0.4, "Mw 7.1", color="orange", fontsize=9)
        ax.set_title(f"{region_name.replace('_', ' ')} first activation")
        ax.set_xlabel("Local x (km)")
        ax.set_ylabel("Local y (km)")
        ax.set_aspect("equal", adjustable="box")
        cbar = fig.colorbar(sc, ax=ax, shrink=0.82)
        cbar.set_label("First activation time since Mw 6.4 (hours)")
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_neighborhood_first_activation_maps(
    neighborhood_tables: dict[str, pd.DataFrame],
    domains: list[CircleDomain],
    main64: Mainshock,
    main71: Mainshock,
    max_hours: float,
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    cmap = truncate_cmap(CMAP_NAME, 0.12, 1.0)
    for ax, domain in zip(axes, domains):
        df = neighborhood_tables[domain.name]
        inactive = df["event_count"] == 0
        active = df["event_count"] > 0
        ax.scatter(df.loc[inactive, "x_km"], df.loc[inactive, "y_km"], s=24, c=ZERO_CELL_COLOR, marker="s", linewidths=0)
        sc = ax.scatter(
            df.loc[active, "x_km"],
            df.loc[active, "y_km"],
            s=24,
            c=df.loc[active, "first_activation_hours"],
            cmap=cmap,
            vmin=0.0,
            vmax=max_hours,
            marker="s",
            linewidths=0,
        )
        ax.add_patch(Circle((domain.center_x_km, domain.center_y_km), domain.radius_km, fill=False, lw=1.2, color="black"))
        ax.scatter([main64.x_km], [main64.y_km], color="red", marker="*", s=130)
        ax.scatter([main71.x_km], [main71.y_km], color="orange", marker="*", s=130)
        ax.text(main64.x_km + 0.4, main64.y_km + 0.4, "Mw 6.4", color="red", fontsize=9)
        ax.text(main71.x_km + 0.4, main71.y_km + 0.4, "Mw 7.1", color="orange", fontsize=9)
        ax.set_title(domain.name.replace("_", " "))
        ax.set_xlabel("Local x (km)")
        ax.set_ylabel("Local y (km)")
        ax.set_aspect("equal", adjustable="box")
        cbar = fig.colorbar(sc, ax=ax, shrink=0.82)
        cbar.set_label("First activation time since Mw 6.4 (hours)")
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_time_along_heatmaps(
    heatmap_tables: dict[str, pd.DataFrame],
    corridors: dict[str, Corridor],
    max_hours: float,
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
    cmap = truncate_cmap(CMAP_NAME, 0.08, 1.0)
    cmap.set_bad(HEATMAP_ZERO_COLOR)
    for ax, region_name in zip(axes, ["Region_A", "Region_B"]):
        df = heatmap_tables[region_name]
        df = df.loc[df["resolution"] == "30min"].copy()
        pivot = df.groupby(["along_km", "bin_start_hours"], as_index=False)["event_count"].sum()
        pivot = pivot.pivot(index="along_km", columns="bin_start_hours", values="event_count").sort_index(axis=0).sort_index(axis=1)
        data = pivot.to_numpy(dtype=float)
        data[data == 0] = np.nan
        extent = [0.0, max_hours, 0.0, corridors[region_name].length_km]
        im = ax.imshow(data, origin="lower", aspect="auto", extent=extent, cmap=cmap, interpolation="nearest")
        ax.set_title(f"{region_name.replace('_', ' ')} time-vs-along-strike count heatmap (30 min)")
        ax.set_xlabel("Time since Mw 6.4 (hours)")
        ax.set_ylabel("Along-strike distance (km)")
        cbar = fig.colorbar(im, ax=ax, shrink=0.82)
        cbar.set_label("Event count per along-strike bin")
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_first_activation_vs_along(
    along_tables: dict[str, pd.DataFrame],
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), constrained_layout=True, sharey=True)
    for ax, region_name in zip(axes, ["Region_A", "Region_B"]):
        df = along_tables[region_name].copy()
        ax.scatter(df["along_bin_center_km"], df["first_activation_hours"], s=24, color="#1f77b4", alpha=0.9)
        if len(df) >= 2 and df["first_activation_hours"].notna().sum() >= 2:
            valid = df.dropna(subset=["first_activation_hours"]) 
            coef = np.polyfit(valid["along_bin_center_km"], valid["first_activation_hours"], 1)
            xfit = np.linspace(valid["along_bin_center_km"].min(), valid["along_bin_center_km"].max(), 200)
            yfit = np.polyval(coef, xfit)
            ax.plot(xfit, yfit, color="black", lw=1.3, ls="--", label=f"Linear trend: {coef[0]:.2f} h/km")
            corr = np.corrcoef(valid["along_bin_center_km"], valid["first_activation_hours"])[0, 1]
            ax.text(0.03, 0.95, f"r = {corr:.2f}", transform=ax.transAxes, va="top")
            ax.legend(loc="upper right")
        ax.set_title(f"{region_name.replace('_', ' ')} first activation vs along strike")
        ax.set_xlabel("Along-strike distance (km)")
        ax.set_ylabel("First activation time since Mw 6.4 (hours)")
        ax.grid(alpha=0.3)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def save_metadata(output_dir: Path, max_hours: float, n_jobs: int) -> None:
    meta = {
        "cell_size_km": CELL_SIZE_KM,
        "corridor_grid_cell_size_km": CELL_SIZE_KM,
        "neighborhood_grid_cell_size_km": CELL_SIZE_KM,
        "time_resolutions_hours": [HALF_HOUR_HOURS, ONE_HOUR_HOURS],
        "first_activation_definition": "first post-Mw6.4 event time in each cell, in hours since Mw 6.4",
        "peak_rate_time_definition": "center of the highest-count bin within the specified resolution",
        "along_strike_bin_km": ALONG_STRIKE_BIN_KM,
        "max_hours_until_Mw7.1": max_hours,
        "parallel_jobs": n_jobs,
    }
    with (output_dir / "metadata" / "gridded_activation_metadata.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def main() -> None:
    try:
        log("Resetting output directory...")
        reset_output_dir(OUTPUT_DIR)

        log("Loading geometry metadata and event assignments...")
        metadata = load_json(GEOMETRY_METADATA_PATH)
        events = pd.read_csv(CATALOG_ASSIGNMENTS_PATH, parse_dates=["event_time"])
        if events.empty:
            raise ValueError("Event assignment table is empty.")

        fwd_transformer, inv_transformer = build_transformers(metadata["local_crs_wkt"])
        main64, main71 = enrich_mainshocks(metadata, fwd_transformer)
        max_hours = float((main71.event_time - main64.event_time).total_seconds() / 3600.0)
        if max_hours <= 0:
            raise ValueError("Mw 7.1 origin time must be later than Mw 6.4 origin time.")

        region_a = make_corridor(metadata["region_a"], fwd_transformer, "Region_A")
        region_b = make_corridor(metadata["region_b"], fwd_transformer, "Region_B")
        corridors = {"Region_A": region_a, "Region_B": region_b}
        domains = build_circle_domains(main64, main71, float(metadata["neighborhood_radius_km"]))

        n_jobs = min(MAX_CORES, max(1, (os.cpu_count() or 1)))
        log(f"Using up to {n_jobs} parallel workers.")

        cell_tables: dict[str, pd.DataFrame] = {}
        heatmap_tables: dict[str, pd.DataFrame] = {}
        along_tables: dict[str, pd.DataFrame] = {}
        for region_name, corridor in corridors.items():
            cell_df, heatmap_df, along_df = corridor_cell_table(
                region_name=region_name,
                events=events,
                corridor=corridor,
                main64=main64,
                main71=main71,
                inv_transformer=inv_transformer,
                max_hours=max_hours,
                n_jobs=n_jobs,
            )
            cell_tables[region_name] = cell_df
            heatmap_tables[region_name] = heatmap_df
            along_tables[region_name] = along_df
            cell_df.to_csv(OUTPUT_DIR / "tables" / f"{region_name.lower()}_cell_activation_table.csv", index=False)
            heatmap_df.to_csv(OUTPUT_DIR / "tables" / f"{region_name.lower()}_time_along_heatmap_table.csv", index=False)
            along_df.to_csv(OUTPUT_DIR / "tables" / f"{region_name.lower()}_along_strike_summary.csv", index=False)

        neighborhood_tables: dict[str, pd.DataFrame] = {}
        for domain in domains:
            df = neighborhood_cell_table(
                domain=domain,
                events=events,
                main64=main64,
                main71=main71,
                inv_transformer=inv_transformer,
                max_hours=max_hours,
                n_jobs=n_jobs,
            )
            neighborhood_tables[domain.name] = df
            df.to_csv(OUTPUT_DIR / "tables" / f"{domain.name.lower()}_cell_activation_table.csv", index=False)

        combined_corridor = pd.concat([cell_tables["Region_A"], cell_tables["Region_B"]], ignore_index=True)
        combined_corridor.to_csv(OUTPUT_DIR / "tables" / "corridor_cell_activation_table_all_regions.csv", index=False)
        combined_neighborhood = pd.concat(list(neighborhood_tables.values()), ignore_index=True)
        combined_neighborhood.to_csv(OUTPUT_DIR / "tables" / "neighborhood_cell_activation_table.csv", index=False)

        log("Generating figures...")
        plot_corridor_cumulative_maps(
            cell_tables=cell_tables,
            corridors=corridors,
            main64=main64,
            main71=main71,
            output_path=OUTPUT_DIR / "figures" / "corridor_cumulative_seismicity_maps.png",
        )
        plot_corridor_first_activation_maps(
            cell_tables=cell_tables,
            corridors=corridors,
            main64=main64,
            main71=main71,
            max_hours=max_hours,
            output_path=OUTPUT_DIR / "figures" / "corridor_first_activation_maps.png",
        )
        plot_neighborhood_first_activation_maps(
            neighborhood_tables=neighborhood_tables,
            domains=domains,
            main64=main64,
            main71=main71,
            max_hours=max_hours,
            output_path=OUTPUT_DIR / "figures" / "neighborhood_first_activation_maps.png",
        )
        plot_time_along_heatmaps(
            heatmap_tables=heatmap_tables,
            corridors=corridors,
            max_hours=max_hours,
            output_path=OUTPUT_DIR / "figures" / "time_vs_along_strike_heatmaps.png",
        )
        plot_first_activation_vs_along(
            along_tables=along_tables,
            output_path=OUTPUT_DIR / "figures" / "first_activation_vs_along_strike.png",
        )

        save_metadata(OUTPUT_DIR, max_hours=max_hours, n_jobs=n_jobs)

        for region_name, df in cell_tables.items():
            if df.empty or int((df["event_count"] > 0).sum()) == 0:
                raise ValueError(f"{region_name} produced no activated cells.")
        log("03_gridded_activation_ordering completed successfully.")
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
