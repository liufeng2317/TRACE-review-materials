from __future__ import annotations

import json
import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


BASE_DIR = Path("<CASE_ROOT>/data")
STEP1_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/01_data_verification_and_rematch")
STEP2_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/02_sequence_extraction")
STEP3_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/03_sequence_diagnostics")
STEP4_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/04_robustness_analysis")
STEP5_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/05_three_sequence_comparison")
STEP6_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/06_control_comparison")
STEP7_OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/07_figure_generation")
OUTPUT_DIR = Path("<CASE_ROOT>/run/02_1_sequence_response/exp_run/outputs/08_reusable_outputs")
FIGURE_DATA_PATH = STEP7_OUTPUT_DIR / "figure_data"
FIGURE_DIR = STEP7_OUTPUT_DIR / "figures"

CATALOG_PATH = BASE_DIR / "catalog/Snet_catalog_relocate.csv"
MAIN_PATH = BASE_DIR / "catalog/main_earthquake.csv"
MECHA_PATH = BASE_DIR / "source_mechanism/Snet_mecha.csv"
STATION_PATH = BASE_DIR / "stations/station.sta"
MATCH_PATH = STEP1_OUTPUT_DIR / "matched_mainshocks.csv"
SEQ_PATH = STEP2_OUTPUT_DIR / "event_centered_sequence_table.csv"
COUNTS_PATH = STEP2_OUTPUT_DIR / "sequence_extraction_counts.csv"
SUMMARY_PATH = STEP3_OUTPUT_DIR / "sequence_diagnostics_metrics.csv"
WINDOW_PATH = STEP3_OUTPUT_DIR / "time_binned_rates.csv"
RADIAL_PATH = STEP3_OUTPUT_DIR / "radial_distance_summary.csv"
DEPTH_PATH = STEP3_OUTPUT_DIR / "depth_distribution_summary.csv"
MAG_PATH = STEP3_OUTPUT_DIR / "magnitude_distribution_summary.csv"
MECHA_SUMMARY_PATH = STEP3_OUTPUT_DIR / "mechanism_overlap_summary.csv"
ROBUSTNESS_INPUT_PATH = STEP3_OUTPUT_DIR / "robustness_summary.csv"
COMPARISON_PATH = STEP3_OUTPUT_DIR / "three_sequence_comparison.csv"
CONTROL_PATH = STEP3_OUTPUT_DIR / "control_summary.csv"
ROBUSTNESS_PATH = STEP4_OUTPUT_DIR / "robustness_results.csv"
SENSITIVITY_PATH = STEP4_OUTPUT_DIR / "sensitivity_summary.csv"
STABILITY_PATH = STEP4_OUTPUT_DIR / "stability_flags.csv"
GRID_PATH = STEP4_OUTPUT_DIR / "parameter_grid_summary.csv"
COMPARISON_BASELINE_PATH = STEP4_OUTPUT_DIR / "three_sequence_comparison_baseline.csv"
CONTROL_BASELINE_PATH = STEP4_OUTPUT_DIR / "control_comparison_baseline.csv"
MASTER_COMPARISON_PATH = STEP5_OUTPUT_DIR / "three_sequence_comparison_master.csv"
BASELINE_COMPARISON_STEP5_PATH = STEP5_OUTPUT_DIR / "three_sequence_comparison_baseline.csv"
CONTROL_SUMMARY_STEP5_PATH = STEP5_OUTPUT_DIR / "control_comparison_summary.csv"
CONTROL_OBS_RAND_PATH = STEP6_OUTPUT_DIR / "control_observed_randomized.csv"
CONTROL_RATIO_PATH = STEP6_OUTPUT_DIR / "control_pairwise_ratio.csv"
CONTROL_SUMMARY_ALT_PATH = STEP6_OUTPUT_DIR / "control_summary.csv"
CONTROL_OBS_RATES_PATH = STEP6_OUTPUT_DIR / "control_observed_rates.csv"
CONTROL_RAND_RATES_PATH = STEP6_OUTPUT_DIR / "control_randomized_rates.csv"
CONTROL_OBS_VS_RAND_SUMMARY_PATH = STEP6_OUTPUT_DIR / "control_observed_vs_randomized_summary.csv"
CONTROL_BACKGROUND_PATH = STEP6_OUTPUT_DIR / "control_background_comparison.csv"

MAINSHOCKS = ["M1", "M2", "M3"]
BASELINE_RADIUS = 50.0
BASELINE_TIME = 90.0
BASELINE_DEPTH = "all"


def log(msg: str) -> None:
    print(msg, flush=True)


def to_jsonable(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (pd.Series, pd.Index)):
        return value.tolist()
    if pd.isna(value):
        return None
    return value


def clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in list(OUTPUT_DIR.iterdir()):
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    FIGURE_DATA_PATH.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    log(f"[0] Cleaned stale artifacts in {OUTPUT_DIR}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return pd.read_csv(path)


def parse_time(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in ["time", "datetime", "matched_datetime", "origin_time", "control_time"]:
        if c in out.columns:
            out[c] = parse_time(out[c])
    for c in ["lat", "lon", "dep", "depth_km", "mag", "mag_1", "mag_2", "latitude", "longitude", "elevation_m"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def load_inputs() -> Dict[str, pd.DataFrame]:
    paths = {
        "catalog": CATALOG_PATH,
        "main": MAIN_PATH,
        "mecha": MECHA_PATH,
        "station": STATION_PATH,
        "match": MATCH_PATH,
        "seq": SEQ_PATH,
        "counts": COUNTS_PATH,
        "summary": SUMMARY_PATH,
        "window": WINDOW_PATH,
        "radial": RADIAL_PATH,
        "depth": DEPTH_PATH,
        "mag": MAG_PATH,
        "mecha_summary": MECHA_SUMMARY_PATH,
        "robustness_input": ROBUSTNESS_INPUT_PATH,
        "comparison": COMPARISON_PATH,
        "control": CONTROL_PATH,
        "robustness": ROBUSTNESS_PATH,
        "sensitivity": SENSITIVITY_PATH,
        "stability": STABILITY_PATH,
        "grid": GRID_PATH,
        "comparison_baseline": COMPARISON_BASELINE_PATH,
        "control_baseline": CONTROL_BASELINE_PATH,
        "master_comparison": MASTER_COMPARISON_PATH,
        "baseline_comparison_step5": BASELINE_COMPARISON_STEP5_PATH,
        "control_summary_step5": CONTROL_SUMMARY_STEP5_PATH,
        "control_summary_alt": CONTROL_SUMMARY_ALT_PATH,
        "control_observed_rates": CONTROL_OBS_RATES_PATH,
        "control_randomized_rates": CONTROL_RAND_RATES_PATH,
        "control_observed_vs_randomized_summary": CONTROL_OBS_VS_RAND_SUMMARY_PATH,
        "control_background_comparison": CONTROL_BACKGROUND_PATH,
    }
    out: Dict[str, pd.DataFrame] = {}
    missing = []
    for key, path in paths.items():
        if not path.exists():
            missing.append(f"{key}: {path}")
        else:
            out[key] = read_csv(path)
    if missing:
        raise FileNotFoundError("Missing required upstream outputs:\n" + "\n".join(missing))
    return out


def make_master_tables(inp: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    tables = {k: normalize_columns(v) for k, v in inp.items()}
    seq = tables["seq"].copy()
    if "sequence_id" not in seq.columns:
        seq["sequence_id"] = np.arange(len(seq), dtype=int)
    if "mainshock" not in seq.columns and "label" in seq.columns:
        seq = seq.rename(columns={"label": "mainshock"})
    if "mag_threshold" in seq.columns:
        seq["mag_threshold_label"] = seq["mag_threshold"].apply(lambda x: "all" if pd.isna(x) else f"M≥{float(x):.1f}")
    else:
        seq["mag_threshold_label"] = "all"
    tables["seq"] = seq
    tables["figure_seq"] = seq[[c for c in ["mainshock", "sequence_id", "event_id", "datetime", "time_rel_days", "lat", "lon", "dep", "mag", "radius_km", "time_window_days", "depth_strategy", "mag_threshold", "pre_post", "radial_distance_km", "depth_rel_km", "mag_threshold_label"] if c in seq.columns]].copy()
    return tables


def build_validation_summary(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name in ["catalog", "main", "match", "seq", "summary", "control"]:
        df = tables[name]
        rows.append({
            "table": name,
            "n_rows": int(len(df)),
            "columns": json.dumps(list(df.columns)),
            "mainshocks": json.dumps(sorted(df["mainshock"].astype(str).unique().tolist()) if "mainshock" in df.columns else []),
        })
    return pd.DataFrame(rows)


def build_dataset_manifest(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.DataFrame([
        {"dataset": key, "n_rows": int(len(df)), "n_cols": int(df.shape[1]), "columns": json.dumps(list(df.columns))}
        for key, df in tables.items()
    ])


def build_reuse_summaries(tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    seq = tables["seq"].copy()
    summary = tables["summary"].copy()
    comparison = tables["comparison"].copy()
    control = tables["control"].copy()
    robustness = tables["robustness"].copy()
    stability = tables["stability"].copy()
    grid = tables["grid"].copy()
    mecha_summary = tables["mecha_summary"].copy()
    baseline = seq[(seq.get("radius_km") == BASELINE_RADIUS) & (seq.get("time_window_days") == BASELINE_TIME)].copy() if not seq.empty else seq.copy()
    return {
        "sequence_feature_table": seq,
        "baseline_sequence_table": baseline,
        "baseline_summary_table": summary[(summary.get("radius_km") == BASELINE_RADIUS) & (summary.get("time_window_days") == BASELINE_TIME)].copy() if not summary.empty else summary.copy(),
        "comparison_table": comparison,
        "control_table": control,
        "robustness_table": robustness,
        "stability_table": stability,
        "grid_table": grid,
        "mechanism_summary_table": mecha_summary,
    }


def write_df(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def write_json(obj, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=to_jsonable)


def write_outputs(tables: Dict[str, pd.DataFrame], reuse: Dict[str, pd.DataFrame]) -> None:
    write_df(tables["seq"], OUTPUT_DIR / "event_centered_sequence_table_master.csv")
    write_df(tables["counts"], OUTPUT_DIR / "sequence_extraction_counts_master.csv")
    write_df(tables["summary"], OUTPUT_DIR / "sequence_diagnostics_metrics_master.csv")
    write_df(tables["window"], OUTPUT_DIR / "time_binned_rates_master.csv")
    write_df(tables["radial"], OUTPUT_DIR / "radial_distance_summary_master.csv")
    write_df(tables["depth"], OUTPUT_DIR / "depth_distribution_summary_master.csv")
    write_df(tables["mag"], OUTPUT_DIR / "magnitude_distribution_summary_master.csv")
    write_df(tables["mecha_summary"], OUTPUT_DIR / "mechanism_overlap_summary_master.csv")
    write_df(tables["robustness_input"], OUTPUT_DIR / "robustness_summary_master.csv")
    write_df(tables["comparison"], OUTPUT_DIR / "three_sequence_comparison_master.csv")
    write_df(tables["control"], OUTPUT_DIR / "control_summary_master.csv")
    write_df(tables["robustness"], OUTPUT_DIR / "robustness_results_master.csv")
    write_df(tables["sensitivity"], OUTPUT_DIR / "sensitivity_summary_master.csv")
    write_df(tables["stability"], OUTPUT_DIR / "stability_flags_master.csv")
    write_df(tables["grid"], OUTPUT_DIR / "parameter_grid_summary_master.csv")
    write_df(tables["comparison_baseline"], OUTPUT_DIR / "three_sequence_comparison_baseline_master.csv")
    write_df(tables["control_baseline"], OUTPUT_DIR / "control_comparison_baseline_master.csv")
    write_df(tables["master_comparison"], OUTPUT_DIR / "three_sequence_comparison_step5_master.csv")
    write_df(tables["baseline_comparison_step5"], OUTPUT_DIR / "three_sequence_comparison_step5_baseline.csv")
    write_df(tables["control_summary_step5"], OUTPUT_DIR / "control_comparison_step5_summary.csv")
    write_df(tables["control_summary_alt"], OUTPUT_DIR / "control_summary_master.csv")
    write_df(tables["control_observed_rates"], OUTPUT_DIR / "control_observed_rates_master.csv")
    write_df(tables["control_randomized_rates"], OUTPUT_DIR / "control_randomized_rates_master.csv")
    write_df(tables["control_observed_vs_randomized_summary"], OUTPUT_DIR / "control_observed_vs_randomized_summary_master.csv")
    write_df(tables["control_background_comparison"], OUTPUT_DIR / "control_background_comparison_master.csv")

    write_df(reuse["sequence_feature_table"], OUTPUT_DIR / "sequence_feature_table.csv")
    write_df(reuse["baseline_sequence_table"], OUTPUT_DIR / "baseline_sequence_table.csv")
    write_df(reuse["baseline_summary_table"], OUTPUT_DIR / "baseline_summary_table.csv")
    write_df(reuse["comparison_table"], OUTPUT_DIR / "comparison_table.csv")
    write_df(reuse["control_table"], OUTPUT_DIR / "control_table.csv")
    write_df(reuse["robustness_table"], OUTPUT_DIR / "robustness_table.csv")
    write_df(reuse["stability_table"], OUTPUT_DIR / "stability_table.csv")
    write_df(reuse["grid_table"], OUTPUT_DIR / "parameter_grid_table.csv")
    write_df(reuse["mechanism_summary_table"], OUTPUT_DIR / "mechanism_summary_table.csv")
    write_df(build_dataset_manifest(tables), OUTPUT_DIR / "dataset_manifest.csv")
    write_df(build_validation_summary(tables), OUTPUT_DIR / "validation_summary.csv")
    write_df(pd.DataFrame({"figure_file": sorted([p.name for p in FIGURE_DIR.glob("*.png")])}), OUTPUT_DIR / "figure_manifest.csv")
    for d in [FIGURE_DATA_PATH]:
        d.mkdir(parents=True, exist_ok=True)
    write_df(reuse["sequence_feature_table"], FIGURE_DATA_PATH / "sequence_feature_table.csv")
    write_df(reuse["baseline_sequence_table"], FIGURE_DATA_PATH / "baseline_sequence_table.csv")
    write_df(reuse["baseline_summary_table"], FIGURE_DATA_PATH / "baseline_summary_table.csv")
    write_df(reuse["comparison_table"], FIGURE_DATA_PATH / "comparison_table.csv")
    write_df(reuse["control_table"], FIGURE_DATA_PATH / "control_table.csv")
    write_df(reuse["robustness_table"], FIGURE_DATA_PATH / "robustness_table.csv")
    write_df(reuse["stability_table"], FIGURE_DATA_PATH / "stability_table.csv")
    write_df(reuse["grid_table"], FIGURE_DATA_PATH / "parameter_grid_table.csv")
    write_df(reuse["mechanism_summary_table"], FIGURE_DATA_PATH / "mechanism_summary_table.csv")


def main() -> None:
    try:
        clean_output_dir()
        inp = load_inputs()
        tables = make_master_tables(inp)
        reuse = build_reuse_summaries(tables)
        write_outputs(tables, reuse)
        verification = {
            "n_catalog": int(len(tables["catalog"])),
            "n_mainshocks": int(len(tables["main"])),
            "n_mechanism_rows": int(len(tables["mecha"])),
            "n_station_rows": int(len(tables["station"])),
            "n_matched_mainshocks": int(len(tables["match"])),
            "n_sequence_rows": int(len(tables["seq"])),
            "n_summary_rows": int(len(tables["summary"])),
            "n_control_rows": int(len(tables["control"])),
            "n_figure_files": int(len(list(FIGURE_DIR.glob("*.png")))),
            "output_files": sorted([p.name for p in OUTPUT_DIR.iterdir() if p.is_file()]),
        }
        write_json(verification, OUTPUT_DIR / "reusable_outputs_verification.json")
        write_json({"generated_files": verification["output_files"], "figure_files": sorted([p.name for p in FIGURE_DIR.glob("*.png")])}, OUTPUT_DIR / "reusable_outputs_manifest.json")
        log(f"[1] Exported reusable tables to {OUTPUT_DIR}")
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
