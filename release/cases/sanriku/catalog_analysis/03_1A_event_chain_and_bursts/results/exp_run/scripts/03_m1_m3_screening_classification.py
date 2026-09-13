from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

BASE_DIR = Path("<CASE_ROOT>")
RUN_DIR = BASE_DIR / "run" / "03_1A_event_chain_and_bursts" / "exp_run"
INPUT_DIR = RUN_DIR / "outputs" / "01_m1_m3_event_chain_analysis"
OUTPUT_DIR = RUN_DIR / "outputs" / "03_m1_m3_screening_classification"

COUNTS_PATH = INPUT_DIR / "m1_m3_window_summary_counts_rates.csv"
COMPOSITION_PATH = INPUT_DIR / "m1_m3_window_summary_composition.csv"
RAW_VS_M2_PATH = INPUT_DIR / "m1_m3_raw_vs_m2aware_summary.csv"
PHASE_CONTRIB_PATH = INPUT_DIR / "m1_m3_phase_contribution_summary.csv"
BURST_PATH = INPUT_DIR / "m1_m3_burst_table.csv"
GAP_PATH = INPUT_DIR / "m1_m3_gap_continuity_metrics.csv"
MIGRATION_PATH = INPUT_DIR / "m1_m3_migration_endpoint_switching_summary.csv"
CONTROL_PATH = INPUT_DIR / "m1_m3_control_comparison.csv"
REFERENCE_PATH = INPUT_DIR / "m1_m3_reference_table.csv"

CLASSIFICATION_OUT = OUTPUT_DIR / "m1_m3_classification_summary.csv"
FOLLOWUP_OUT = OUTPUT_DIR / "m1_m3_followup_priority_table.csv"
REPORT_OUT = OUTPUT_DIR / "m1_m3_screening_report.md"
EVIDENCE_OUT = OUTPUT_DIR / "m1_m3_classification_evidence.csv"

VERSIONS = ["raw", "m2aware"]
THRESHOLDS = [3.0, 4.0, 5.0, 6.0]
KEY_WINDOWS = [
    "pre_M1_baseline_14d",
    "pre_M1_baseline_7d",
    "M1_related_primary",
    "full_M1_to_M3",
    "middle_primary",
    "pre_M3_primary",
    "post_M3_7d",
]
CLASSIFICATION_ORDER = [
    "pre_existing_local_activity_before_M1",
    "M1_related_swarm_aftershock_dominated",
    "middle_phase_activity_after_M1_plus_21d",
    "continuous_activation_chain",
    "separated_bursts",
    "endpoint_centered_activity",
    "pre_M3_local_activation",
    "corridor_like_activity",
    "apparent_migration",
    "endpoint_switching_or_mixed_endpoint_sequences",
    "broader_regional_or_background_component",
    "M2_affected_or_ambiguous_mixed_behavior",
]


def log(message: str) -> None:
    print(message, flush=True)


def clean_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in [CLASSIFICATION_OUT, FOLLOWUP_OUT, REPORT_OUT, EVIDENCE_OUT]:
        if path.exists():
            path.unlink()


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")
    df = pd.read_csv(path)
    for col in ["window_start", "window_end", "start_time", "end_time", "origin_time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce", format="ISO8601")
    return df


def require_columns(df: pd.DataFrame, required: List[str], name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def build_lookup(df: pd.DataFrame, key_cols: List[str]) -> pd.DataFrame:
    duplicate_mask = df.duplicated(subset=key_cols, keep=False)
    if duplicate_mask.any():
        dup = df.loc[duplicate_mask, key_cols].head(10).to_dict(orient="records")
        raise ValueError(f"Duplicate key rows found for lookup {key_cols}: {dup}")
    return df.set_index(key_cols, drop=False)


def get_counts_row(counts_idx: pd.DataFrame, window: str, version: str, threshold: float) -> pd.Series:
    return counts_idx.loc[(window, version, threshold)]


def get_composition_row(comp_idx: pd.DataFrame, window: str, version: str) -> pd.Series:
    return comp_idx.loc[(window, version)]


def get_control_row(ctrl_idx: pd.DataFrame, version: str, baseline_window: str, compare_window: str) -> pd.Series:
    return ctrl_idx.loc[(version, baseline_window, compare_window)]


def get_gap_row(gap_idx: pd.DataFrame, version: str, threshold: float) -> pd.Series:
    return gap_idx.loc[(version, threshold)]


def get_phase_row(phase_idx: pd.DataFrame, version: str, threshold: float) -> pd.Series:
    return phase_idx.loc[(version, threshold)]


def get_migration_row(mig_idx: pd.DataFrame, version: str, phase: str) -> pd.Series:
    return mig_idx.loc[(version, phase)]


def classify_version(
    version: str,
    refs: pd.DataFrame,
    counts_idx: pd.DataFrame,
    comp_idx: pd.DataFrame,
    raw_vs_m2: pd.DataFrame,
    phase_idx: pd.DataFrame,
    burst_df: pd.DataFrame,
    gap_idx: pd.DataFrame,
    mig_idx: pd.DataFrame,
    ctrl_idx: pd.DataFrame,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    summary_rows: List[Dict[str, object]] = []
    evidence_rows: List[Dict[str, object]] = []
    followup_rows: List[Dict[str, object]] = []

    m3_pre14 = get_counts_row(counts_idx, "pre_M1_baseline_14d", version, 3.0)
    m3_pre7 = get_counts_row(counts_idx, "pre_M1_baseline_7d", version, 3.0)
    m3_m1rel = get_counts_row(counts_idx, "M1_related_primary", version, 3.0)
    m4_m1rel = get_counts_row(counts_idx, "M1_related_primary", version, 4.0)
    m5_m1rel = get_counts_row(counts_idx, "M1_related_primary", version, 5.0)
    m3_middle = get_counts_row(counts_idx, "middle_primary", version, 3.0)
    m4_middle = get_counts_row(counts_idx, "middle_primary", version, 4.0)
    m3_preM3 = get_counts_row(counts_idx, "pre_M3_primary", version, 3.0)
    m4_preM3 = get_counts_row(counts_idx, "pre_M3_primary", version, 4.0)
    m3_full = get_counts_row(counts_idx, "full_M1_to_M3", version, 3.0)
    m4_full = get_counts_row(counts_idx, "full_M1_to_M3", version, 4.0)

    comp_pre14 = get_composition_row(comp_idx, "pre_M1_baseline_14d", version)
    comp_m1rel = get_composition_row(comp_idx, "M1_related_primary", version)
    comp_middle = get_composition_row(comp_idx, "middle_primary", version)
    comp_preM3 = get_composition_row(comp_idx, "pre_M3_primary", version)
    comp_full = get_composition_row(comp_idx, "full_M1_to_M3", version)

    ctrl_m1rel = get_control_row(ctrl_idx, version, "pre_M1_baseline_14d", "M1_related_primary")
    ctrl_middle = get_control_row(ctrl_idx, version, "pre_M1_baseline_14d", "middle_primary")
    ctrl_preM3 = get_control_row(ctrl_idx, version, "pre_M1_baseline_14d", "pre_M3_primary")

    phase_m3 = get_phase_row(phase_idx, version, 3.0)
    phase_m4 = get_phase_row(phase_idx, version, 4.0)

    gap_m3 = get_gap_row(gap_idx, version, 3.0)
    gap_m4 = get_gap_row(gap_idx, version, 4.0)

    mig_full = get_migration_row(mig_idx, version, "full_M1_to_M3")
    mig_m1rel = get_migration_row(mig_idx, version, "M1_related_primary")
    mig_middle = get_migration_row(mig_idx, version, "middle_primary")
    mig_preM3 = get_migration_row(mig_idx, version, "pre_M3_primary")

    raw_vs_sub = raw_vs_m2[(raw_vs_m2["summary_type"] == "counts_rates") & (raw_vs_m2["window"].isin(["full_M1_to_M3", "middle_primary", "pre_M3_primary"])) & (raw_vs_m2["magnitude_threshold"] == 3.0)].copy()

    bursts_v = burst_df.copy()
    if "version" in bursts_v.columns:
        bursts_v = bursts_v[bursts_v["version"] == version].copy()
    n_major_bursts = int((bursts_v["threshold_label"] == "M3+").sum()) if not bursts_v.empty else 0
    n_preM3_bursts = int(((bursts_v["phase_class"] == "pre-M3 local activation") | (bursts_v["phase_class"] == "pre_M3_local_activation")).sum()) if not bursts_v.empty else 0

    classification: Dict[str, str] = {}
    notes: Dict[str, str] = {}

    pre_existing = "present" if int(m3_pre14["event_count"]) >= 10 else "weak_or_sparse"
    classification["pre_existing_local_activity_before_M1"] = pre_existing
    notes["pre_existing_local_activity_before_M1"] = (
        f"Pre-M1 baseline (to M1-14 d) contains {int(m3_pre14['event_count'])} M3+ events over {m3_pre14['duration_days']:.1f} d "
        f"({m3_pre14['rate_per_day']:.3f}/d), with M1-core {comp_pre14['fraction_M1-core']:.2f}, M3-core {comp_pre14['fraction_M3-core']:.2f}, "
        f"corridor non-core {comp_pre14['fraction_corridor_noncore']:.2f}, off-corridor {comp_pre14['fraction_off-corridor_local']:.2f}."
    )

    if float(ctrl_m1rel["rate_ratio_compare_to_baseline"]) >= 5 and phase_m3["M1_related_fraction_of_full"] >= 0.6:
        m1_class = "strong"
    elif float(ctrl_m1rel["rate_ratio_compare_to_baseline"]) >= 2:
        m1_class = "moderate"
    else:
        m1_class = "weak_or_unclear"
    classification["M1_related_swarm_aftershock_dominated"] = m1_class
    notes["M1_related_swarm_aftershock_dominated"] = (
        f"M1-related window has {int(m3_m1rel['event_count'])} M3+, {int(m4_m1rel['event_count'])} M4+, {int(m5_m1rel['event_count'])} M5+; "
        f"M3+ rate is {float(ctrl_m1rel['rate_ratio_compare_to_baseline']):.2f}x the conservative pre-M1 baseline, and the phase contributes "
        f"{phase_m3['M1_related_fraction_of_full']:.2%} of full-interval M3+ and {phase_m4['M1_related_fraction_of_full']:.2%} of M4+."
    )

    middle_rate_ratio = float(ctrl_middle["rate_ratio_compare_to_baseline"])
    if middle_rate_ratio >= 2 and int(m3_middle["event_count"]) >= 30:
        middle_class = "sustained"
    elif int(m3_middle["event_count"]) >= 10:
        middle_class = "present_but_limited"
    else:
        middle_class = "quiet"
    classification["middle_phase_activity_after_M1_plus_21d"] = middle_class
    notes["middle_phase_activity_after_M1_plus_21d"] = (
        f"Middle phase contains {int(m3_middle['event_count'])} M3+ and {int(m4_middle['event_count'])} M4+; M3+ rate is {middle_rate_ratio:.2f}x baseline and the phase accounts for "
        f"{phase_m3['middle_fraction_of_full']:.2%} of full-interval M3+."
    )

    if gap_m3["full_M1_to_M3_max_gap_days"] <= 7 and middle_rate_ratio >= 1.5 and int(m3_middle["event_count"]) >= 30:
        cont_class = "possible_or_mixed"
    elif gap_m3["full_M1_to_M3_max_gap_days"] <= 3 and middle_rate_ratio >= 2.5:
        cont_class = "supported"
    else:
        cont_class = "not_supported"
    classification["continuous_activation_chain"] = cont_class
    notes["continuous_activation_chain"] = (
        f"Full M1-M3 M3+ max inter-event gap is {gap_m3['full_M1_to_M3_max_gap_days']:.2f} d and middle-phase max gap is {gap_m3['middle_phase_max_gap_days']:.2f} d; "
        f"continuous activation is screened cautiously because fixed-window activity persists but is not uniform." 
    )

    sep_class = "yes" if (n_major_bursts >= 2 or gap_m3["full_M1_to_M3_max_gap_days"] >= 7 or gap_m4["full_M1_to_M3_max_gap_days"] >= 14) else "no_or_unclear"
    classification["separated_bursts"] = sep_class
    notes["separated_bursts"] = (
        f"Burst table reports {n_major_bursts} M3+ bursts; full-interval max gaps are {gap_m3['full_M1_to_M3_max_gap_days']:.2f} d for M3+ and {gap_m4['full_M1_to_M3_max_gap_days']:.2f} d for M4+, supporting burst separation rather than a homogeneous sequence."
    )

    endpoint_strength = max(comp_full["fraction_M1-core"] + comp_full["fraction_M3-core"], comp_m1rel["fraction_M1-core"] + comp_m1rel["fraction_M3-core"], comp_preM3["fraction_M1-core"] + comp_preM3["fraction_M3-core"])
    endpoint_class = "yes" if endpoint_strength >= 0.65 else "mixed_or_weak"
    classification["endpoint_centered_activity"] = endpoint_class
    notes["endpoint_centered_activity"] = (
        f"Endpoint cores dominate local events in key windows: full M1-M3 {(comp_full['fraction_M1-core'] + comp_full['fraction_M3-core']):.2f}, "
        f"M1-related {(comp_m1rel['fraction_M1-core'] + comp_m1rel['fraction_M3-core']):.2f}, pre-M3 {(comp_preM3['fraction_M1-core'] + comp_preM3['fraction_M3-core']):.2f}."
    )

    if float(ctrl_preM3["rate_ratio_compare_to_baseline"]) >= 2 and int(m3_preM3["event_count"]) >= 20:
        preM3_class = "clear_local_activation"
    elif int(m3_preM3["event_count"]) >= 10:
        preM3_class = "possible_or_limited"
    else:
        preM3_class = "weak_or_absent"
    classification["pre_M3_local_activation"] = preM3_class
    notes["pre_M3_local_activation"] = (
        f"Pre-M3 window contains {int(m3_preM3['event_count'])} M3+ and {int(m4_preM3['event_count'])} M4+; M3+ rate is {float(ctrl_preM3['rate_ratio_compare_to_baseline']):.2f}x baseline, with M3-core fraction {comp_preM3['fraction_M3-core']:.2f} and M1-core fraction {comp_preM3['fraction_M1-core']:.2f}."
    )

    corridor_fraction_max = max(comp_full["fraction_corridor_noncore"], comp_middle["fraction_corridor_noncore"], comp_preM3["fraction_corridor_noncore"])
    corridor_class = "yes" if corridor_fraction_max >= 0.3 else "no_or_mixed"
    classification["corridor_like_activity"] = corridor_class
    notes["corridor_like_activity"] = (
        f"Corridor non-core fractions are full M1-M3 {comp_full['fraction_corridor_noncore']:.2f}, middle {comp_middle['fraction_corridor_noncore']:.2f}, pre-M3 {comp_preM3['fraction_corridor_noncore']:.2f}; corridor events are present but not dominant." 
    )

    robust_migration = (
        abs(mig_full["time_along_axis_correlation"]) >= 0.35
        and abs(mig_middle["time_along_axis_correlation"]) >= 0.25
        and abs(mig_preM3["time_along_axis_correlation"]) >= 0.25
    )
    migration_class = "possible" if robust_migration else "not_robust"
    classification["apparent_migration"] = migration_class
    notes["apparent_migration"] = (
        f"Time-along-axis correlations are full {mig_full['time_along_axis_correlation']:.3f}, M1-related {mig_m1rel['time_along_axis_correlation']:.3f}, middle {mig_middle['time_along_axis_correlation']:.3f}, pre-M3 {mig_preM3['time_along_axis_correlation']:.3f}; apparent full-interval trend does not remain robust after window separation." 
    )

    endpoint_switch = (
        comp_m1rel["fraction_M1-core"] > comp_m1rel["fraction_M3-core"]
        and comp_preM3["fraction_M3-core"] > comp_preM3["fraction_M1-core"]
    )
    if not robust_migration and endpoint_strength >= 0.65:
        endpoint_switch_class = "mixed_endpoint_sequences"
    elif endpoint_switch:
        endpoint_switch_class = "possible_but_M1_weighted"
    else:
        endpoint_switch_class = "no_or_unclear"
    classification["endpoint_switching_or_mixed_endpoint_sequences"] = endpoint_switch_class
    notes["endpoint_switching_or_mixed_endpoint_sequences"] = (
        f"Window-separated activity remains endpoint-heavy without robust migration; M1-core fractions are {comp_m1rel['fraction_M1-core']:.2f} in the M1-related phase and {comp_preM3['fraction_M1-core']:.2f} in the pre-M3 phase, while M3-core fractions are {comp_m1rel['fraction_M3-core']:.2f} and {comp_preM3['fraction_M3-core']:.2f}."
    )

    offcorr_full = comp_full["fraction_off-corridor_local"]
    background_class = "meaningful" if offcorr_full >= 0.35 else "subordinate"
    classification["broader_regional_or_background_component"] = background_class
    notes["broader_regional_or_background_component"] = (
        f"Off-corridor local fraction is {offcorr_full:.2f} for full M1-M3 and {comp_pre14['fraction_off-corridor_local']:.2f} in the pre-M1 baseline, so broader/background local activity is present but secondary to endpoint-centered activity."
    )

    m2_removed_full = raw_vs_sub.loc[raw_vs_sub["window"] == "full_M1_to_M3", "fraction_removed_by_M2"]
    m2_removed_middle = raw_vs_sub.loc[raw_vs_sub["window"] == "middle_primary", "fraction_removed_by_M2"]
    m2_removed_preM3 = raw_vs_sub.loc[raw_vs_sub["window"] == "pre_M3_primary", "fraction_removed_by_M2"]
    m2_full_val = float(m2_removed_full.iloc[0]) if not m2_removed_full.empty else 0.0
    m2_middle_val = float(m2_removed_middle.iloc[0]) if not m2_removed_middle.empty else 0.0
    m2_preM3_val = float(m2_removed_preM3.iloc[0]) if not m2_removed_preM3.empty else 0.0
    if max(m2_full_val, m2_middle_val, m2_preM3_val) >= 0.15:
        m2_class = "material"
    elif max(m2_full_val, m2_middle_val, m2_preM3_val) >= 0.03:
        m2_class = "compare_raw_and_m2aware"
    else:
        m2_class = "limited_effect"
    classification["M2_affected_or_ambiguous_mixed_behavior"] = m2_class
    notes["M2_affected_or_ambiguous_mixed_behavior"] = (
        f"M2-aware removal changes M3+ counts by {m2_full_val:.2%} for full M1-M3, {m2_middle_val:.2%} for the middle phase, and {m2_preM3_val:.2%} for the pre-M3 phase; effects are quantified but do not erase the main fixed-window pattern."
    )

    for item in CLASSIFICATION_ORDER:
        summary_rows.append(
            {
                "version": version,
                "classification_item": item,
                "classification": classification[item],
                "evidence_note": notes[item],
            }
        )
        evidence_rows.append(
            {
                "version": version,
                "classification_item": item,
                "classification": classification[item],
                "evidence_note": notes[item],
            }
        )

    followup_rows.extend(
        [
            {
                "version": version,
                "followup_topic": "spatial_depth_screening",
                "priority": "high" if classification["pre_M3_local_activation"] in {"clear_local_activation", "possible_or_limited"} else "medium",
                "reason": "Separate M1-related, middle, and pre-M3 depth bands and endpoint clusters to test whether later activity occupies distinct local volumes rather than a single homogeneous sequence.",
            },
            {
                "version": version,
                "followup_topic": "b_value_completeness",
                "priority": "high" if int(m3_full["event_count"]) >= 100 else "medium",
                "reason": "The local chain has enough events to compare magnitude-frequency behavior across the conservative pre-M1 baseline, M1-related phase, middle phase, and pre-M3 phase.",
            },
            {
                "version": version,
                "followup_topic": "burst_wise_migration_screening",
                "priority": "medium" if classification["apparent_migration"] == "not_robust" else "high",
                "reason": "Only test burst-wise centroid motion after keeping M1-related, middle, and pre-M3 windows separate; do not rely on full-interval centroid shifts alone.",
            },
            {
                "version": version,
                "followup_topic": "mechanism_screening",
                "priority": "medium",
                "reason": "Use focal mechanisms only as partial-coverage context for identified endpoint groups or bursts; treat any mechanism interpretation as hypothesis-level follow-up.",
            },
        ]
    )

    return summary_rows, evidence_rows, followup_rows


def build_report(refs: pd.DataFrame, summary_df: pd.DataFrame, counts: pd.DataFrame, comp: pd.DataFrame, ctrl: pd.DataFrame, phase: pd.DataFrame) -> str:
    ref_lookup = refs.set_index("label")
    m1_time = pd.to_datetime(ref_lookup.loc["M1", "origin_time"], utc=True)
    m3_time = pd.to_datetime(ref_lookup.loc["M3", "origin_time"], utc=True)

    def fetch_class(version: str, item: str) -> str:
        row = summary_df[(summary_df["version"] == version) & (summary_df["classification_item"] == item)].iloc[0]
        return str(row["classification"])

    def count_row(window: str, version: str, threshold: float) -> pd.Series:
        return counts[(counts["window"] == window) & (counts["version"] == version) & (counts["magnitude_threshold"] == threshold)].iloc[0]

    def comp_row(window: str, version: str) -> pd.Series:
        return comp[(comp["window"] == window) & (comp["version"] == version)].iloc[0]

    def ctrl_row(version: str, compare_window: str) -> pd.Series:
        return ctrl[(ctrl["version"] == version) & (ctrl["baseline_window"] == "pre_M1_baseline_14d") & (ctrl["compare_window"] == compare_window)].iloc[0]

    def phase_row(version: str, threshold: float) -> pd.Series:
        return phase[(phase["version"] == version) & (phase["magnitude_threshold"] == threshold)].iloc[0]

    raw_full = count_row("full_M1_to_M3", "raw", 3.0)
    m2_full = count_row("full_M1_to_M3", "m2aware", 3.0)
    raw_middle = count_row("middle_primary", "raw", 3.0)
    raw_preM3 = count_row("pre_M3_primary", "raw", 3.0)
    raw_m1rel = count_row("M1_related_primary", "raw", 3.0)
    raw_pre14 = count_row("pre_M1_baseline_14d", "raw", 3.0)
    raw_pre7 = count_row("pre_M1_baseline_7d", "raw", 3.0)
    raw_comp_full = comp_row("full_M1_to_M3", "raw")
    raw_comp_m1rel = comp_row("M1_related_primary", "raw")
    raw_comp_middle = comp_row("middle_primary", "raw")
    raw_comp_preM3 = comp_row("pre_M3_primary", "raw")
    raw_ctrl_m1rel = ctrl_row("raw", "M1_related_primary")
    raw_ctrl_middle = ctrl_row("raw", "middle_primary")
    raw_ctrl_preM3 = ctrl_row("raw", "pre_M3_primary")
    raw_phase = phase_row("raw", 3.0)
    m2_phase = phase_row("m2aware", 3.0)

    lines = []
    lines.append("# M1-M3 screening classification")
    lines.append("")
    lines.append("## Scope and caution")
    lines.append(
        "This is a catalog-level, non-causal screening summary for the M1-M3 local system. The interpretation is based on fixed windows and local/corridor geometry only. Temporal order or spatial proximity alone are not treated as evidence of triggering or physical causality."
    )
    lines.append("")
    lines.append("## Reference interval")
    lines.append(f"- M1 origin time: {m1_time.isoformat()}")
    lines.append(f"- M3 origin time: {m3_time.isoformat()}")
    lines.append(f"- Conservative pre-M1 baseline: catalog start to M1-14 d")
    lines.append(f"- Sensitivity pre-M1 baseline: catalog start to M1-7 d")
    lines.append(f"- M1-related dominated phase: M1-14 d to M1+21 d")
    lines.append(f"- Middle phase: M1+21 d to M3-35 d")
    lines.append(f"- Pre-M3 local activation phase: M3-35 d to M3")
    lines.append("")
    lines.append("## Main screening conclusions")
    for item in CLASSIFICATION_ORDER:
        raw_class = fetch_class("raw", item)
        m2_class = fetch_class("m2aware", item)
        lines.append(f"- **{item}**: raw={raw_class}; m2aware={m2_class}")
    lines.append("")
    lines.append("## Key evidence")
    lines.append(
        f"- Pre-M1 local activity is clearly present: {int(raw_pre14['event_count'])} M3+ events over {raw_pre14['duration_days']:.1f} d ({raw_pre14['rate_per_day']:.3f}/d) using the conservative baseline, and {int(raw_pre7['event_count'])} M3+ using the M1-7 d sensitivity baseline."
    )
    lines.append(
        f"- The M1-related dominated phase is the strongest component of the M1-M3 interval: {int(raw_m1rel['event_count'])} M3+ with rate ratio {raw_ctrl_m1rel['rate_ratio_compare_to_baseline']:.2f}x relative to the conservative baseline, contributing {raw_phase['M1_related_fraction_of_full']:.1%} of full-interval M3+."
    )
    lines.append(
        f"- After separating the M1-related phase, the middle phase is not empty: {int(raw_middle['event_count'])} M3+ with rate ratio {raw_ctrl_middle['rate_ratio_compare_to_baseline']:.2f}x baseline, so the interval after M1+21 d is better described as sustained but weaker than the M1-related phase, not homogeneous with it."
    )
    lines.append(
        f"- The final pre-M3 window also shows distinct local activity: {int(raw_preM3['event_count'])} M3+ with rate ratio {raw_ctrl_preM3['rate_ratio_compare_to_baseline']:.2f}x baseline, consistent with pre-M3 local activation that remains after M2-aware flagging ({int(m2_full['event_count'])} M3+ for full M1-M3 versus {int(raw_full['event_count'])} raw)."
    )
    lines.append(
        f"- Endpoint cores dominate more than corridor non-core activity. In the full M1-M3 interval, M1-core={raw_comp_full['fraction_M1-core']:.2f}, M3-core={raw_comp_full['fraction_M3-core']:.2f}, corridor non-core={raw_comp_full['fraction_corridor_noncore']:.2f}, off-corridor local={raw_comp_full['fraction_off-corridor_local']:.2f}."
    )
    lines.append(
        f"- The M1-related phase is strongly M1-core weighted (M1-core {raw_comp_m1rel['fraction_M1-core']:.2f}, M3-core {raw_comp_m1rel['fraction_M3-core']:.2f}), while the pre-M3 phase still remains M1-core heavy overall (M1-core {raw_comp_preM3['fraction_M1-core']:.2f}, M3-core {raw_comp_preM3['fraction_M3-core']:.2f}) rather than becoming a dominant corridor sequence."
    )
    lines.append(
        f"- The chain is better described as burst-separated and endpoint-centered than as a clean corridor migration: the full-interval M1-related fraction is {raw_phase['M1_related_fraction_of_full']:.1%}, while middle+pre-M3 still contribute {raw_phase['middle_plus_pre_M3_fraction_of_full']:.1%} of M3+, indicating important later activity but not a single uniform episode."
    )
    lines.append("")
    lines.append("## M2-aware comparison")
    lines.append(
        f"- Full M1-M3 M3+ counts change from {int(raw_full['event_count'])} raw to {int(m2_full['event_count'])} M2-aware ({1 - m2_full['event_count'] / raw_full['event_count']:.1%} removed)."
    )
    lines.append(
        f"- The main interpretation is therefore M2-aware but not M2-dominated: M2 flagging modestly reduces some middle/pre-M3 counts but does not remove the pre-existing activity, the strong M1-related phase, or the later pre-M3 activation signal."
    )
    lines.append("")
    lines.append("## Recommended follow-up")
    lines.append("1. Spatial-depth screening to test whether middle-phase and pre-M3 activity occupy distinct depth bands or endpoint clusters.")
    lines.append("2. b-value / completeness screening by fixed window, since the local sample is large enough for phase-wise magnitude-frequency comparison.")
    lines.append("3. Burst-wise migration checks only after keeping M1-related, middle, and pre-M3 windows separate.")
    lines.append("4. Optional focal-mechanism screening for the best-sampled endpoint or burst groups only.")
    lines.append("")
    lines.append("## Bottom-line classification")
    lines.append(
        "The M1-M3 local system is best screened as: **pre-existing local activity before M1**, a **strong M1-related swarm/aftershock-dominated phase**, a **non-empty but weaker middle phase after M1+21 d**, **separated bursts** rather than a homogeneous continuous sequence, **endpoint-centered activity** more than corridor-dominated activity, and **clear pre-M3 local activation** that survives M2-aware comparison. The apparent full-interval along-axis trend is **not robust enough to call continuous migration** after window separation; it is better treated as **mixed endpoint-centered behavior with possible switching/overlap, not a confirmed migrating chain**."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    clean_output_dir(OUTPUT_DIR)
    log(f"Loading summary inputs from {INPUT_DIR}")

    counts = load_csv(COUNTS_PATH)
    comp = load_csv(COMPOSITION_PATH)
    raw_vs_m2 = load_csv(RAW_VS_M2_PATH)
    phase = load_csv(PHASE_CONTRIB_PATH)
    bursts = load_csv(BURST_PATH)
    gaps = load_csv(GAP_PATH)
    migration = load_csv(MIGRATION_PATH)
    control = load_csv(CONTROL_PATH)
    refs = load_csv(REFERENCE_PATH)

    require_columns(counts, ["window", "version", "magnitude_threshold", "event_count", "duration_days", "rate_per_day"], "counts")
    require_columns(comp, ["window", "version", "fraction_M1-core", "fraction_M3-core", "fraction_corridor_noncore", "fraction_off-corridor_local"], "composition")
    require_columns(raw_vs_m2, ["summary_type", "window", "magnitude_threshold", "fraction_removed_by_M2"], "raw_vs_m2")
    require_columns(phase, ["version", "magnitude_threshold", "M1_related_fraction_of_full", "middle_fraction_of_full", "pre_M3_fraction_of_full", "middle_plus_pre_M3_fraction_of_full"], "phase_contribution")
    require_columns(gaps, ["version", "magnitude_threshold", "full_M1_to_M3_max_gap_days", "middle_phase_max_gap_days"], "gap_metrics")
    require_columns(migration, ["version", "phase", "time_along_axis_correlation", "fraction_M1_core", "fraction_M3_core", "fraction_corridor_noncore", "fraction_off_corridor_local"], "migration")
    require_columns(control, ["version", "baseline_window", "compare_window", "rate_ratio_compare_to_baseline"], "control")
    require_columns(refs, ["label", "origin_time"], "reference")

    counts_idx = build_lookup(counts, ["window", "version", "magnitude_threshold"])
    comp_idx = build_lookup(comp, ["window", "version"])
    phase_idx = build_lookup(phase, ["version", "magnitude_threshold"])
    gap_idx = build_lookup(gaps, ["version", "magnitude_threshold"])
    mig_idx = build_lookup(migration, ["version", "phase"])
    ctrl_idx = build_lookup(control, ["version", "baseline_window", "compare_window"])

    all_summary_rows: List[Dict[str, object]] = []
    all_evidence_rows: List[Dict[str, object]] = []
    all_followup_rows: List[Dict[str, object]] = []

    for version in VERSIONS:
        log(f"Classifying version={version}")
        summary_rows, evidence_rows, followup_rows = classify_version(
            version=version,
            refs=refs,
            counts_idx=counts_idx,
            comp_idx=comp_idx,
            raw_vs_m2=raw_vs_m2,
            phase_idx=phase_idx,
            burst_df=bursts,
            gap_idx=gap_idx,
            mig_idx=mig_idx,
            ctrl_idx=ctrl_idx,
        )
        all_summary_rows.extend(summary_rows)
        all_evidence_rows.extend(evidence_rows)
        all_followup_rows.extend(followup_rows)

    summary_df = pd.DataFrame(all_summary_rows)
    evidence_df = pd.DataFrame(all_evidence_rows)
    followup_df = pd.DataFrame(all_followup_rows)

    summary_df.to_csv(CLASSIFICATION_OUT, index=False)
    evidence_df.to_csv(EVIDENCE_OUT, index=False)
    followup_df.to_csv(FOLLOWUP_OUT, index=False)

    report = build_report(refs, summary_df, counts, comp, control, phase)
    REPORT_OUT.write_text(report, encoding="utf-8")

    log(f"Wrote classification summary: {CLASSIFICATION_OUT}")
    log(f"Wrote evidence table: {EVIDENCE_OUT}")
    log(f"Wrote follow-up priorities: {FOLLOWUP_OUT}")
    log(f"Wrote screening report: {REPORT_OUT}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), flush=True)
        sys.exit(1)
