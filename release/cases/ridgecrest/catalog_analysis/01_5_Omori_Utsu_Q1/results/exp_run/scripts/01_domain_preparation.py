from __future__ import annotations

import json
import math
import os
import sys
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import CRS, Transformer


CATALOG_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/TRACE_ridgecrest_relocated.csv')
MAINSHOCK_PATH = Path('<REPO_ROOT>/examples/ridgecrest/data/catalog_TRACE/main_shock_events.csv')
OUTPUT_DIR = Path('<REPO_ROOT>/examples/ridgecrest/catalog_analysis/run/01_5_trigger_Omori_Utsu_Q1-v2/exp_run/outputs/01_domain_preparation')

EVENT_TABLE_CSV = OUTPUT_DIR / 'interevent_domain_event_table.csv'
DOMAIN_COUNT_CSV = OUTPUT_DIR / 'domain_counts_primary.csv'
DOMAIN_CHECK_CSV = OUTPUT_DIR / 'domain_assignment_checks.csv'
METADATA_JSON = OUTPUT_DIR / 'domain_metadata.json'
FIGURE_PATH = OUTPUT_DIR / 'domain_assignment_diagnostic.png'
OUTPUT_FILES = [EVENT_TABLE_CSV, DOMAIN_COUNT_CSV, DOMAIN_CHECK_CSV, METADATA_JSON, FIGURE_PATH]

PRIMARY_SPLIT_LAT = 35.72
SPLIT_LATS = [35.70, 35.72, 35.74]
PRIMARY_MAG_THRESHOLD = 3.0
M54_SEPARATOR_DAYS = 0.732
FINAL_PERIOD_DAYS = 1.404
STRIKE_DEG = 138.0
CORRIDOR_WIDTH_KM = 8.0
HALF_WIDTH_KM = CORRIDOR_WIDTH_KM / 2.0
CENTERLINE_START_LON = -117.735813
CENTERLINE_START_LAT = 35.897499
CENTERLINE_END_LON = -117.362520
CENTERLINE_END_LAT = 35.559488
TIME_COL = 'event_time'


@dataclass
class CorridorGeometry:
    strike_deg: float
    centerline_start_lon: float
    centerline_start_lat: float
    centerline_end_lon: float
    centerline_end_lat: float
    total_width_km: float
    half_width_km: float
    centerline_length_km: float


def log(message: str) -> None:
    print(message, flush=True)


def build_local_transformer() -> tuple[Transformer, Transformer, CRS]:
    lon0 = (CENTERLINE_START_LON + CENTERLINE_END_LON) / 2.0
    lat0 = (CENTERLINE_START_LAT + CENTERLINE_END_LAT) / 2.0
    crs_local = CRS.from_proj4(
        f'+proj=aeqd +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=m +no_defs'
    )
    forward = Transformer.from_crs('EPSG:4326', crs_local, always_xy=True)
    inverse = Transformer.from_crs(crs_local, 'EPSG:4326', always_xy=True)
    return forward, inverse, crs_local


def read_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    log(f'Reading catalog: {CATALOG_PATH}')
    catalog = pd.read_csv(CATALOG_PATH)
    log(f'Reading mainshocks: {MAINSHOCK_PATH}')
    mainshocks = pd.read_csv(MAINSHOCK_PATH)
    expected = ['event_time', 'latitude', 'longitude', 'depth_km', 'magnitude']
    if list(catalog.columns) != expected:
        raise ValueError(f'Unexpected catalog columns: {catalog.columns.tolist()}')
    if list(mainshocks.columns) != expected:
        raise ValueError(f'Unexpected mainshock columns: {mainshocks.columns.tolist()}')
    return catalog, mainshocks


def identify_mainshocks(mainshocks: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    ms64 = mainshocks.loc[np.isclose(mainshocks['magnitude'], 6.4)]
    ms71 = mainshocks.loc[np.isclose(mainshocks['magnitude'], 7.1)]
    if len(ms64) != 1 or len(ms71) != 1:
        raise ValueError('Could not uniquely identify Mw 6.4 and Mw 7.1 mainshocks.')
    return ms64.iloc[0], ms71.iloc[0]


def project_points(df: pd.DataFrame, transformer: Transformer) -> pd.DataFrame:
    x_m, y_m = transformer.transform(df['longitude'].to_numpy(), df['latitude'].to_numpy())
    out = df.copy()
    out['x_m'] = x_m
    out['y_m'] = y_m
    out['x_km'] = out['x_m'] / 1000.0
    out['y_km'] = out['y_m'] / 1000.0
    return out


def assign_corridor_domains(interevent: pd.DataFrame, transformer: Transformer) -> tuple[pd.DataFrame, CorridorGeometry, dict[str, np.ndarray]]:
    sx, sy = transformer.transform(CENTERLINE_START_LON, CENTERLINE_START_LAT)
    ex, ey = transformer.transform(CENTERLINE_END_LON, CENTERLINE_END_LAT)
    start = np.array([sx, sy], dtype=float)
    end = np.array([ex, ey], dtype=float)
    vec = end - start
    length_m = float(np.hypot(vec[0], vec[1]))
    if not np.isfinite(length_m) or length_m <= 0:
        raise ValueError('Invalid centerline length.')
    u = vec / length_m
    left_normal = np.array([-u[1], u[0]], dtype=float)

    pts = interevent[['x_m', 'y_m']].to_numpy(dtype=float)
    rel = pts - start[None, :]
    along_m = rel @ u
    cross_m = rel @ left_normal

    in_segment = (along_m >= 0.0) & (along_m <= length_m)
    in_width = np.abs(cross_m) <= HALF_WIDTH_KM * 1000.0
    in_entire = in_segment & in_width

    out = interevent.copy()
    out['along_strike_km'] = along_m / 1000.0
    out['cross_strike_km'] = cross_m / 1000.0
    out['in_entire_corridor'] = in_entire

    lat = out['latitude'].to_numpy()
    for split in SPLIT_LATS:
        token = f'{split:.2f}'.replace('.', 'p')
        out[f'on_split_{token}'] = np.zeros(len(out), dtype=bool)
        out[f'north_{token}'] = in_entire & (lat > split)
        out[f'south_{token}'] = in_entire & (lat < split)

    corners = np.array([
        start + left_normal * HALF_WIDTH_KM * 1000.0,
        end + left_normal * HALF_WIDTH_KM * 1000.0,
        end - left_normal * HALF_WIDTH_KM * 1000.0,
        start - left_normal * HALF_WIDTH_KM * 1000.0,
        start + left_normal * HALF_WIDTH_KM * 1000.0,
    ])

    geometry = CorridorGeometry(
        strike_deg=STRIKE_DEG,
        centerline_start_lon=CENTERLINE_START_LON,
        centerline_start_lat=CENTERLINE_START_LAT,
        centerline_end_lon=CENTERLINE_END_LON,
        centerline_end_lat=CENTERLINE_END_LAT,
        total_width_km=CORRIDOR_WIDTH_KM,
        half_width_km=HALF_WIDTH_KM,
        centerline_length_km=length_m / 1000.0,
    )
    plot_arrays = {
        'centerline_xy_m': np.vstack([start, end]),
        'corridor_polygon_xy_m': corners,
    }
    return out, geometry, plot_arrays


def make_domain_counts(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append({'domain_label': 'Entire area', 'split_latitude_deg': PRIMARY_SPLIT_LAT, 'event_count_all_magnitudes': int(df['in_entire_corridor'].sum())})
    rows.append({'domain_label': 'Northern area', 'split_latitude_deg': PRIMARY_SPLIT_LAT, 'event_count_all_magnitudes': int(df['north_35p72'].sum())})
    rows.append({'domain_label': 'Southern area', 'split_latitude_deg': PRIMARY_SPLIT_LAT, 'event_count_all_magnitudes': int(df['south_35p72'].sum())})
    out = pd.DataFrame(rows)
    out['event_count_m_ge_3'] = [
        int((df['in_entire_corridor'] & (df['magnitude'] >= PRIMARY_MAG_THRESHOLD)).sum()),
        int((df['north_35p72'] & (df['magnitude'] >= PRIMARY_MAG_THRESHOLD)).sum()),
        int((df['south_35p72'] & (df['magnitude'] >= PRIMARY_MAG_THRESHOLD)).sum()),
    ]
    return out


def make_assignment_checks(df: pd.DataFrame) -> pd.DataFrame:
    north_all = int(df['north_35p72'].sum())
    south_all = int(df['south_35p72'].sum())
    onsplit_all = int(df['on_split_35p72'].sum())
    entire_all = int(df['in_entire_corridor'].sum())
    checks = [
        ('all_interevent_events', len(df)),
        ('entire_corridor_all_magnitudes', entire_all),
        ('north_35p72_all_magnitudes', north_all),
        ('south_35p72_all_magnitudes', south_all),
        ('on_split_35p72_all_magnitudes', onsplit_all),
        ('north_plus_south_35p72_all_magnitudes', north_all + south_all),
        ('north_plus_south_minus_entire_35p72_all_magnitudes', (north_all + south_all) - entire_all),
        ('entire_corridor_m_ge_3', int((df['in_entire_corridor'] & (df['magnitude'] >= PRIMARY_MAG_THRESHOLD)).sum())),
        ('north_35p72_m_ge_3', int((df['north_35p72'] & (df['magnitude'] >= PRIMARY_MAG_THRESHOLD)).sum())),
        ('south_35p72_m_ge_3', int((df['south_35p72'] & (df['magnitude'] >= PRIMARY_MAG_THRESHOLD)).sum())),
    ]
    return pd.DataFrame(checks, columns=['check_name', 'value'])


def plot_diagnostic(interevent: pd.DataFrame, mainshocks_proj: pd.DataFrame, plot_arrays: dict[str, np.ndarray], inverse: Transformer) -> None:
    log(f'Creating diagnostic figure: {FIGURE_PATH}')
    fig, ax = plt.subplots(figsize=(8.8, 7.6), constrained_layout=True)

    scatter = ax.scatter(
        interevent['longitude'],
        interevent['latitude'],
        c=interevent['t_days'],
        s=8,
        cmap='viridis',
        alpha=0.65,
        linewidths=0,
        label='All interevent events',
        zorder=1,
    )

    entire = interevent.loc[interevent['in_entire_corridor']]
    north = interevent.loc[interevent['north_35p72']]
    south = interevent.loc[interevent['south_35p72']]

    ax.scatter(entire['longitude'], entire['latitude'], s=14, facecolors='none', edgecolors='0.35', linewidths=0.6, label='Entire corridor events', zorder=2)
    ax.scatter(north['longitude'], north['latitude'], s=16, c='tab:blue', alpha=0.85, linewidths=0, label='Northern area', zorder=3)
    ax.scatter(south['longitude'], south['latitude'], s=16, c='tab:red', alpha=0.85, linewidths=0, label='Southern area', zorder=3)

    centerline = plot_arrays['centerline_xy_m']
    center_lon, center_lat = inverse.transform(centerline[:, 0], centerline[:, 1])
    ax.plot(center_lon, center_lat, color='k', lw=1.8, label='Mw 7.1 centerline', zorder=4)

    polygon = plot_arrays['corridor_polygon_xy_m']
    poly_lon, poly_lat = inverse.transform(polygon[:, 0], polygon[:, 1])
    ax.plot(poly_lon, poly_lat, color='k', lw=1.0, ls='--', label='8 km corridor boundary', zorder=4)

    lon_min = min(interevent['longitude'].min(), poly_lon.min(), mainshocks_proj['longitude'].min()) - 0.02
    lon_max = max(interevent['longitude'].max(), poly_lon.max(), mainshocks_proj['longitude'].max()) + 0.02
    ax.hlines(PRIMARY_SPLIT_LAT, lon_min, lon_max, color='magenta', lw=1.5, ls=':', label='35.72°N split', zorder=4)

    ms64 = mainshocks_proj.loc[np.isclose(mainshocks_proj['magnitude'], 6.4)].iloc[0]
    ms71 = mainshocks_proj.loc[np.isclose(mainshocks_proj['magnitude'], 7.1)].iloc[0]
    ax.scatter(ms64['longitude'], ms64['latitude'], marker='*', s=220, c='gold', edgecolors='k', linewidths=0.8, label='Mw 6.4 mainshock', zorder=5)
    ax.scatter(ms71['longitude'], ms71['latitude'], marker='*', s=240, c='orange', edgecolors='k', linewidths=0.8, label='Mw 7.1 mainshock', zorder=5)

    cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
    cbar.set_label('Time since Mw 6.4 [day]')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Ridgecrest interevent domain assignment for fixed Mw 7.1 fault-zone corridor')
    ax.set_xlim(lon_min, lon_max)
    lat_min = min(interevent['latitude'].min(), poly_lat.min(), mainshocks_proj['latitude'].min()) - 0.02
    lat_max = max(interevent['latitude'].max(), poly_lat.max(), mainshocks_proj['latitude'].max()) + 0.02
    ax.set_ylim(lat_min, lat_max)
    ax.grid(True, color='0.9', linewidth=0.7)
    ax.legend(loc='best', fontsize=8, frameon=True)

    fig.savefig(FIGURE_PATH, dpi=220)
    plt.close(fig)


def remove_stale_outputs() -> None:
    for path in OUTPUT_FILES:
        if path.exists():
            log(f'Removing stale output: {path}')
            path.unlink()



def validate_required_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns in {label}: {missing}')



def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log(f'Output directory: {OUTPUT_DIR}')
    remove_stale_outputs()

    catalog, mainshocks = read_inputs()
    validate_required_columns(catalog, ['event_time', 'latitude', 'longitude', 'depth_km', 'magnitude'], 'catalog')
    validate_required_columns(mainshocks, ['event_time', 'latitude', 'longitude', 'depth_km', 'magnitude'], 'mainshocks')

    catalog[TIME_COL] = pd.to_datetime(catalog[TIME_COL], utc=True)
    mainshocks[TIME_COL] = pd.to_datetime(mainshocks[TIME_COL], utc=True)

    ms64, ms71 = identify_mainshocks(mainshocks)
    t0 = ms64[TIME_COL]
    t71 = ms71[TIME_COL]
    if not (t71 > t0):
        raise ValueError('Mw 7.1 origin time must be after Mw 6.4 origin time.')

    log(f'Mw 6.4 origin time: {t0.isoformat()}')
    log(f'Mw 7.1 origin time: {t71.isoformat()}')

    catalog['t_days'] = (catalog[TIME_COL] - t0).dt.total_seconds() / 86400.0
    interevent = catalog.loc[(catalog[TIME_COL] > t0) & (catalog[TIME_COL] < t71)].copy()
    interevent.sort_values(TIME_COL, inplace=True)
    interevent.reset_index(drop=False, inplace=True)
    interevent.rename(columns={'index': 'source_row_index'}, inplace=True)
    log(f'Interevent events retained: {len(interevent)}')

    forward, inverse, local_crs = build_local_transformer()
    interevent = project_points(interevent, forward)
    mainshocks_proj = project_points(mainshocks.copy(), forward)
    interevent, geometry, plot_arrays = assign_corridor_domains(interevent, forward)
    validate_required_columns(
        interevent,
        [
            'source_row_index', 'event_time', 'latitude', 'longitude', 'depth_km', 'magnitude', 't_days',
            'x_km', 'y_km', 'along_strike_km', 'cross_strike_km', 'in_entire_corridor',
            'north_35p70', 'south_35p70', 'on_split_35p70',
            'north_35p72', 'south_35p72', 'on_split_35p72',
            'north_35p74', 'south_35p74', 'on_split_35p74',
        ],
        'interevent domain table',
    )

    checks = make_assignment_checks(interevent)
    entire = int(interevent['in_entire_corridor'].sum())
    north = int(interevent['north_35p72'].sum())
    south = int(interevent['south_35p72'].sum())
    onsplit = int(interevent['on_split_35p72'].sum())
    if north + south != entire:
        raise ValueError('Primary strict north/south split accounting does not match entire corridor count.')
    if onsplit != 0:
        log(f'Note: on_split_35p72 diagnostic count is {onsplit}, but strict domain assignment follows exact > / < partitioning from source latitudes.')

    domain_counts = make_domain_counts(interevent)

    event_columns = [
        'source_row_index', 'event_time', 'latitude', 'longitude', 'depth_km', 'magnitude', 't_days',
        'x_km', 'y_km', 'along_strike_km', 'cross_strike_km', 'in_entire_corridor',
        'north_35p70', 'south_35p70', 'on_split_35p70',
        'north_35p72', 'south_35p72', 'on_split_35p72',
        'north_35p74', 'south_35p74', 'on_split_35p74'
    ]
    interevent_to_save = interevent[event_columns].copy()
    interevent_to_save['event_time'] = interevent_to_save['event_time'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    log(f'Saving event table: {EVENT_TABLE_CSV}')
    interevent_to_save.to_csv(EVENT_TABLE_CSV, index=False)
    log(f'Saving domain counts: {DOMAIN_COUNT_CSV}')
    domain_counts.to_csv(DOMAIN_COUNT_CSV, index=False)
    log(f'Saving assignment checks: {DOMAIN_CHECK_CSV}')
    checks.to_csv(DOMAIN_CHECK_CSV, index=False)

    metadata = {
        'mw64_time_utc': t0.isoformat(),
        'mw71_time_utc': t71.isoformat(),
        'm54_separator_period_days': M54_SEPARATOR_DAYS,
        'final_period_days': FINAL_PERIOD_DAYS,
        'primary_magnitude_threshold': PRIMARY_MAG_THRESHOLD,
        'primary_split_latitude_deg': PRIMARY_SPLIT_LAT,
        'robustness_split_latitudes_deg': SPLIT_LATS,
        'catalog_path': str(CATALOG_PATH),
        'mainshock_path': str(MAINSHOCK_PATH),
        'local_projection_wkt_snippet': local_crs.to_wkt()[:500],
        'corridor_geometry': asdict(geometry),
        'interevent_event_count_all_magnitudes': int(len(interevent)),
        'interevent_event_count_m_ge_3': int((interevent['magnitude'] >= PRIMARY_MAG_THRESHOLD).sum()),
        'primary_domain_counts': domain_counts.to_dict(orient='records'),
    }
    log(f'Saving metadata: {METADATA_JSON}')
    with open(METADATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    plot_diagnostic(interevent, mainshocks_proj, plot_arrays, inverse)
    log('01_domain_preparation completed successfully.')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
