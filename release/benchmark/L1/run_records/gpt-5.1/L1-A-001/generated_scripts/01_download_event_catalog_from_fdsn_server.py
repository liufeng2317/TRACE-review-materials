#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
01_download_event_catalog_from_fdsn_server.py

Download an earthquake catalog from an FDSN server using the `seismostats`
FDSNWSEventClient, assemble results into a pandas DataFrame and a
seismostats Catalog, save the catalog to CSV, and plot epicenters in space.

All outputs are saved in the specified output directory.
"""

import os
import sys
from typing import Dict, Any

import pandas as pd
import matplotlib.pyplot as plt

from seismostats.catalogs.client import FDSNWSEventClient
from seismostats import Catalog


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


def get_config() -> Dict[str, Any]:
    """
    Return configuration parameters for the catalog download and output paths.
    """
    output_dir = "<OUTPUT_ROOT>"

    return {
        # Query parameters
        "start_time_str": "2020-01-01T00:00:00",
        "end_time_str": "2022-01-01T00:00:00",
        "min_longitude": 5.0,
        "max_longitude": 11.0,
        "min_latitude": 45.0,
        "max_latitude": 48.0,
        "min_magnitude": 0.5,
        "batch_size": 1000,
        "fdsn_url": "http://eida.ethz.ch/fdsnws/event/1/query",
        # Output paths
        "output_dir": output_dir,
        "catalog_csv": os.path.join(output_dir, "earthquake_catalog.csv"),
        "catalog_png": os.path.join(output_dir, "earthquake_catalog.png"),
    }


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def parse_and_validate_parameters(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse time strings to pandas Timestamps and validate basic constraints.
    """
    start_time = pd.to_datetime(cfg["start_time_str"])
    end_time = pd.to_datetime(cfg["end_time_str"])

    if start_time >= end_time:
        raise ValueError(
            f"start_time ({start_time}) must be earlier than end_time ({end_time})"
        )

    min_lon = cfg["min_longitude"]
    max_lon = cfg["max_longitude"]
    min_lat = cfg["min_latitude"]
    max_lat = cfg["max_latitude"]
    min_mag = cfg["min_magnitude"]

    if min_lon >= max_lon:
        raise ValueError(
            f"min_longitude ({min_lon}) must be less than max_longitude ({max_lon})"
        )
    if min_lat >= max_lat:
        raise ValueError(
            f"min_latitude ({min_lat}) must be less than max_latitude ({max_lat})"
        )
    if min_mag < 0.0:
        raise ValueError(
            f"min_magnitude ({min_mag}) must be non-negative"
        )

    cfg["start_time"] = start_time
    cfg["end_time"] = end_time
    return cfg


def initialize_fdsn_client(fdsn_url: str) -> FDSNWSEventClient:
    """
    Initialize the FDSNWS event client from seismostats.
    """
    client = FDSNWSEventClient(fdsn_url)
    return client


def download_events_in_batches(client: FDSNWSEventClient, cfg: Dict[str, Any]) -> Catalog:
    """
    Use FDSNWSEventClient to download events matching the given constraints,
    using batched retrieval.
    """
    try:
        catalog = client.get_events(
            start_time=cfg["start_time"],
            end_time=cfg["end_time"],
            min_magnitude=cfg["min_magnitude"],
            min_longitude=cfg["min_longitude"],
            max_longitude=cfg["max_longitude"],
            min_latitude=cfg["min_latitude"],
            max_latitude=cfg["max_latitude"],
            batch_size=cfg["batch_size"],
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to download events from {cfg['fdsn_url']} "
            f"for time window {cfg['start_time']} - {cfg['end_time']}"
        ) from exc

    if catalog is None or len(catalog) == 0:
        print("No events found for the specified constraints.")
    else:
        print(f"Downloaded {len(catalog)} events from FDSN server.")

    return catalog


def validate_and_clean_catalog(catalog: Catalog) -> pd.DataFrame:
    """
    Validate the Catalog and normalize essential columns into a pandas DataFrame.
    """
    # Catalog in seismostats is DataFrame-like, but we explicitly convert.
    df = pd.DataFrame(catalog)

    if df.empty:
        return df

    required_cols = {"time", "latitude", "longitude"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(
            f"The downloaded catalog is missing required columns: {missing}"
        )

    # Convert types
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    if "magnitude" in df.columns:
        df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")

    # Drop rows with invalid coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    # Sort by time if available
    if "time" in df.columns:
        df = df.sort_values("time").reset_index(drop=True)

    return df


def construct_seismostats_catalog(df: pd.DataFrame) -> Catalog:
    """
    Construct a seismostats Catalog object from a pandas DataFrame.
    """
    catalog = Catalog(df)
    return catalog


def export_catalog_to_csv(catalog: Catalog, csv_path: str) -> None:
    """
    Save the catalog to a CSV file (without index).
    """
    try:
        catalog.to_csv(csv_path, index=False)
        print(f"Catalog saved to CSV: {csv_path}")
    except Exception as exc:
        raise IOError(f"Failed to write catalog CSV to {csv_path}") from exc


def plot_catalog_in_space(
    catalog: Catalog,
    cfg: Dict[str, Any],
) -> None:
    """
    Generate and save a spatial plot (longitude vs latitude) of epicenters.
    """
    png_path = cfg["catalog_png"]

    if len(catalog) == 0:
        print("Catalog is empty; skipping spatial plot.")
        return

    # Ensure we have numeric lon/lat
    df = pd.DataFrame(catalog).copy()
    df = df.dropna(subset=["longitude", "latitude"])

    if df.empty:
        print("No valid longitude/latitude data to plot; skipping plot.")
        return

    lons = pd.to_numeric(df["longitude"], errors="coerce")
    lats = pd.to_numeric(df["latitude"], errors="coerce")

    mask = (~lons.isna()) & (~lats.isna())
    lons = lons[mask]
    lats = lats[mask]

    if lons.empty or lats.empty:
        print("No valid coordinates after cleaning; skipping plot.")
        return

    plt.figure(figsize=(6, 6))
    plt.scatter(lons, lats, s=5.0, alpha=0.7, edgecolor="none")

    plt.xlabel("Longitude (deg)")
    plt.ylabel("Latitude (deg)")
    plt.title(
        f"Earthquakes {cfg['start_time_str']}–{cfg['end_time_str']}, "
        f"M≥{cfg['min_magnitude']}"
    )

    # Set axis limits to query region
    plt.xlim(cfg["min_longitude"], cfg["max_longitude"])
    plt.ylim(cfg["min_latitude"], cfg["max_latitude"])

    plt.tight_layout()
    try:
        plt.savefig(png_path, dpi=300)
        print(f"Spatial catalog plot saved to: {png_path}")
    except Exception as exc:
        raise IOError(f"Failed to save plot to {png_path}") from exc
    finally:
        plt.close()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main() -> None:
    cfg = get_config()

    # Ensure output directory exists
    os.makedirs(cfg["output_dir"], exist_ok=True)

    # Parse and validate parameters
    try:
        cfg = parse_and_validate_parameters(cfg)
    except Exception as exc:
        print(f"Parameter validation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = initialize_fdsn_client(cfg["fdsn_url"])
    print(f"Initialized FDSN client for URL: {cfg['fdsn_url']}")

    # Download events (batched)
    try:
        raw_catalog = download_events_in_batches(client, cfg)
    except Exception as exc:
        print(f"Error while downloading events: {exc}", file=sys.stderr)
        sys.exit(1)

    # Validate and clean to DataFrame
    df_events = validate_and_clean_catalog(raw_catalog)

    # Construct final Catalog from cleaned DataFrame
    catalog = construct_seismostats_catalog(df_events)
    n_events = len(catalog)
    print(f"Number of events after cleaning: {n_events}")

    # Export to CSV
    try:
        export_catalog_to_csv(catalog, cfg["catalog_csv"])
    except Exception as exc:
        print(f"Error while saving catalog to CSV: {exc}", file=sys.stderr)
        sys.exit(1)

    # Plot in space
    try:
        plot_catalog_in_space(catalog, cfg)
    except Exception as exc:
        print(f"Error while plotting catalog: {exc}", file=sys.stderr)
        sys.exit(1)

    # Summary
    print("\nSummary:")
    print(f"  Events in final catalog: {n_events}")
    print(f"  Catalog CSV: {cfg['catalog_csv']}")
    print(f"  Catalog plot PNG: {cfg['catalog_png']}")


if __name__ == "__main__":
    main()
