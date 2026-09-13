from __future__ import annotations

import shutil
import sys
import traceback
from pathlib import Path
from typing import Dict, List

import pandas as pd


BASE_DIR = Path("<CASE_ROOT>")
ANALYSIS_DIR = BASE_DIR / "run/02_3_relationship_screening/exp_run/outputs/01_relationship_analysis"
OUTPUT_DIR = BASE_DIR / "run/02_3_relationship_screening/exp_run/outputs/02_report_synthesis"

PAIR_ORDER = ["M1_M2", "M1_M3", "M2_M3"]
PAIR_LABELS = {"M1_M2": "M1-M2", "M1_M3": "M1-M3", "M2_M3": "M2-M3"}
HYPOTHESIS_ORDER = [
    "independent_local_clusters",
    "overlapping_activation_zones",
    "delayed_activation_between_clusters",
    "linked_local_fault_system_activation",
    "corridor_like_migration_or_expansion",
    "broader_regional_activation",
    "compound_swarm_like_multi_event_clustering",
    "apparent_relationship_from_background_or_window_choices",
    "common_regional_rate_pulse_without_pair_specific_linkage",
]
HYPOTHESIS_LABELS = {
    "independent_local_clusters": "independent local clusters",
    "overlapping_activation_zones": "overlapping activation zones",
    "delayed_activation_between_clusters": "delayed activation between clusters",
    "linked_local_fault_system_activation": "linked local fault-system activation",
    "corridor_like_migration_or_expansion": "corridor-like migration or expansion",
    "broader_regional_activation": "broader regional activation",
    "compound_swarm_like_multi_event_clustering": "compound/swarm-like multi-event clustering",
    "apparent_relationship_from_background_or_window_choices": "apparent relationship from burst-like background or window choices",
    "common_regional_rate_pulse_without_pair_specific_linkage": "common regional rate pulse without pair-specific linkage",
}
PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}
EVIDENCE_ORDER = {"strong": 4, "moderate": 3, "possible": 2, "low": 1}
TABLE_OUTPUTS = [
    "pairwise_scientific_summary.csv",
    "relationship_evidence_matrix_concise.csv",
    "followup_priorities_concise.csv",
    "raw_corrected_distance_summary.csv",
    "strongest_supported_signals.csv",
    "weak_negative_unresolved_signals.csv",
    "recommended_next_steps_ranked.csv",
    "report_manifest.csv",
]
FIGURES_TO_COPY = [
    "fig_pairwise_overview_map.png",
    "fig_pairwise_time_projection.png",
    "fig_intervening_event_chains.png",
    "fig_corridor_vs_control.png",
    "fig_relationship_evidence_matrix.png",
    "fig_followup_priority.png",
]


def log(message: str) -> None:
    print(message, flush=True)



def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for pattern in TABLE_OUTPUTS + ["final_scientific_report.md", "executive_summary.txt"] + FIGURES_TO_COPY:
        path = OUTPUT_DIR / pattern
        if path.exists():
            path.unlink()
            log(f"Removed stale output: {path}")



REQUIRED_COLUMNS = {
    "pairwise_relationship_summary": [
        "pair_name", "mag_subset", "n_events", "n_between_mainshocks", "n_corridor", "n_outer_band",
        "corridor_fraction", "ambiguous_fraction", "shared_fraction", "post_pre_a_ratio", "post_pre_b_ratio",
    ],
    "pair_hypothesis_evidence_matrix": [
        "pair_name", "hypothesis", "raw_score", "corrected_score", "distance_score",
        "raw_evidence", "control_corrected_evidence", "distance_aware_plausibility", "mechanism_context",
    ],
    "followup_priority_table": ["pair_name", "hypothesis", "followup_priority", "recommended_followup"],
    "recommended_next_steps": ["pair_name", "hypothesis", "followup_priority", "recommended_followup"],
    "pairwise_control_corrected_metrics": [
        "pair_name", "mag_subset", "temporal_effect_between", "temporal_effect_corridor_between",
        "between_count_control_pct", "corridor_between_control_pct", "geometric_corridor_effect",
        "pseudo_corridor_pct", "corridor_vs_sideband_control_ratio",
    ],
    "pairwise_distance_aware_plausibility": [
        "pair_name", "pair_sep_km", "pair_depth_diff_km", "pair_time_sep_days",
        "distance_link_score", "depth_penalty", "time_penalty",
    ],
    "regional_activation_summary": ["metric", "value"],
    "mainshock_pair_geometry": ["pair_name", "pair_time_sep_days", "pair_sep_km", "pair_depth_diff_km"],
    "assignment_stability_summary": ["pair_name", "stable_fraction"],
}



def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required input not found: {path}")



def require_columns(df: pd.DataFrame, required: List[str], table_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {table_name}: {missing}")



def load_inputs() -> Dict[str, pd.DataFrame]:
    files = {
        "pairwise_relationship_summary": ANALYSIS_DIR / "pairwise_relationship_summary.csv",
        "pair_hypothesis_evidence_matrix": ANALYSIS_DIR / "pair_hypothesis_evidence_matrix.csv",
        "followup_priority_table": ANALYSIS_DIR / "followup_priority_table.csv",
        "recommended_next_steps": ANALYSIS_DIR / "recommended_next_steps.csv",
        "pairwise_control_corrected_metrics": ANALYSIS_DIR / "pairwise_control_corrected_metrics.csv",
        "pairwise_distance_aware_plausibility": ANALYSIS_DIR / "pairwise_distance_aware_plausibility.csv",
        "regional_activation_summary": ANALYSIS_DIR / "regional_activation_summary.csv",
        "mainshock_pair_geometry": ANALYSIS_DIR / "mainshock_pair_geometry.csv",
        "assignment_stability_summary": ANALYSIS_DIR / "assignment_stability_summary.csv",
    }
    for path in files.values():
        require_file(path)
    data = {name: pd.read_csv(path) for name, path in files.items()}
    for table_name, required in REQUIRED_COLUMNS.items():
        if table_name in data:
            require_columns(data[table_name], required, table_name)
    return data



def ordered_pairs(df: pd.DataFrame, pair_col: str = "pair_name") -> pd.DataFrame:
    temp = df.copy()
    temp["_pair_order"] = temp[pair_col].map({k: i for i, k in enumerate(PAIR_ORDER)})
    if "hypothesis" in temp.columns:
        temp["_hyp_order"] = temp["hypothesis"].map({k: i for i, k in enumerate(HYPOTHESIS_ORDER)})
        temp = temp.sort_values(["_pair_order", "_hyp_order"], kind="stable")
        return temp.drop(columns=["_pair_order", "_hyp_order"])
    temp = temp.sort_values(["_pair_order"], kind="stable")
    return temp.drop(columns=["_pair_order"])



def collect_pair_summary(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    raw = data["pairwise_relationship_summary"].copy()
    raw_all = raw[raw["mag_subset"] == "all"].copy()
    raw_m4 = raw[raw["mag_subset"] == "M4plus"].copy()
    raw_m5 = raw[raw["mag_subset"] == "M5plus"].copy()
    ctrl = data["pairwise_control_corrected_metrics"].copy()
    ctrl_all = ctrl[ctrl["mag_subset"] == "all"].copy()
    ctrl_m4 = ctrl[ctrl["mag_subset"] == "M4plus"].copy()
    dist = data["pairwise_distance_aware_plausibility"].copy()
    assign = data["assignment_stability_summary"].copy()
    geom = data["mainshock_pair_geometry"].copy()

    summary = raw_all.merge(
        raw_m4[["pair_name", "n_events", "n_between_mainshocks", "n_corridor", "n_outer_band", "ambiguous_fraction", "corridor_fraction", "shared_fraction", "post_pre_a_ratio", "post_pre_b_ratio"]].rename(
            columns={
                "n_events": "m4_n_events",
                "n_between_mainshocks": "m4_between_count",
                "n_corridor": "m4_corridor_count",
                "n_outer_band": "m4_outer_count",
                "ambiguous_fraction": "m4_ambiguous_fraction",
                "corridor_fraction": "m4_corridor_fraction",
                "shared_fraction": "m4_shared_fraction",
                "post_pre_a_ratio": "m4_post_pre_a_ratio",
                "post_pre_b_ratio": "m4_post_pre_b_ratio",
            }
        ),
        on="pair_name",
        how="left",
    )
    summary = summary.merge(
        raw_m5[["pair_name", "n_events", "n_outer_band"]].rename(columns={"n_events": "m5_n_events", "n_outer_band": "m5_outer_count"}),
        on="pair_name",
        how="left",
    )
    summary = summary.merge(
        ctrl_all[["pair_name", "temporal_effect_between", "between_count_control_pct", "geometric_corridor_effect", "pseudo_corridor_pct", "corridor_vs_sideband_control_ratio"]].rename(
            columns={
                "temporal_effect_between": "all_temporal_effect_between",
                "between_count_control_pct": "all_between_count_control_pct",
                "geometric_corridor_effect": "all_geometric_corridor_effect",
                "pseudo_corridor_pct": "all_pseudo_corridor_pct",
                "corridor_vs_sideband_control_ratio": "all_corridor_vs_sideband_control_ratio",
            }
        ),
        on="pair_name",
        how="left",
    )
    summary = summary.merge(
        ctrl_m4[["pair_name", "temporal_effect_between", "temporal_effect_corridor_between", "between_count_control_pct", "corridor_between_control_pct", "geometric_corridor_effect", "pseudo_corridor_pct", "corridor_vs_sideband_control_ratio"]].rename(
            columns={
                "temporal_effect_between": "m4_temporal_effect_between",
                "temporal_effect_corridor_between": "m4_temporal_effect_corridor_between",
                "between_count_control_pct": "m4_between_count_control_pct",
                "corridor_between_control_pct": "m4_corridor_between_control_pct",
                "geometric_corridor_effect": "m4_geometric_corridor_effect",
                "pseudo_corridor_pct": "m4_pseudo_corridor_pct",
                "corridor_vs_sideband_control_ratio": "m4_corridor_vs_sideband_control_ratio",
            }
        ),
        on="pair_name",
        how="left",
    )
    summary = summary.merge(dist, on="pair_name", how="left", suffixes=("", "_dist"))
    summary = summary.merge(assign[["pair_name", "stable_fraction"]], on="pair_name", how="left")
    summary = summary.merge(geom[["pair_name", "pair_time_sep_days", "pair_sep_km", "pair_depth_diff_km"]], on="pair_name", how="left", suffixes=("", "_geom"))

    for base_col in ["pair_sep_km", "pair_depth_diff_km", "pair_time_sep_days"]:
        dist_col = f"{base_col}_dist"
        geom_col = f"{base_col}_geom"
        if base_col not in summary.columns:
            if dist_col in summary.columns:
                summary[base_col] = summary[dist_col]
            elif geom_col in summary.columns:
                summary[base_col] = summary[geom_col]
        if base_col not in summary.columns:
            raise ValueError(f"Missing required merged geometry column: {base_col}")

    summary["pair_label"] = summary["pair_name"].map(PAIR_LABELS)
    summary["raw_signal_level"] = summary.apply(
        lambda r: "high"
        if (pd.notna(r["m4_between_count"]) and r["m4_between_count"] >= 40) or (pd.notna(r["m4_corridor_fraction"]) and r["m4_corridor_fraction"] >= 0.35)
        else ("medium" if pd.notna(r["m4_between_count"]) and r["m4_between_count"] >= 10 else "low"),
        axis=1,
    )
    summary["control_screen"] = summary.apply(
        lambda r: "survives_controls"
        if pd.notna(r["m4_between_count_control_pct"]) and pd.notna(r["m4_pseudo_corridor_pct"]) and r["m4_between_count_control_pct"] >= 0.6 and r["m4_pseudo_corridor_pct"] >= 0.6
        else ("partly_weakened" if pd.notna(r["m4_between_count_control_pct"]) and (r["m4_between_count_control_pct"] >= 0.3 or r["m4_pseudo_corridor_pct"] >= 0.3) else "weak_or_control_explained"),
        axis=1,
    )
    summary["distance_plausibility_screen"] = summary["distance_link_score"].apply(
        lambda x: "nearby_plausible" if pd.notna(x) and x >= 0.5 else ("regional_only_or_limited" if pd.notna(x) and x >= 0.2 else "not_local_linkage_plausible")
    )

    keep_cols = [
        "pair_name", "pair_label", "pair_sep_km", "pair_depth_diff_km", "pair_time_sep_days",
        "n_events", "n_between_mainshocks", "n_corridor", "n_outer_band", "corridor_fraction", "ambiguous_fraction",
        "m4_n_events", "m4_between_count", "m4_corridor_count", "m4_outer_count", "m4_ambiguous_fraction", "m4_corridor_fraction", "m4_shared_fraction",
        "m4_post_pre_a_ratio", "m4_post_pre_b_ratio", "m5_n_events", "m5_outer_count",
        "m4_temporal_effect_between", "m4_temporal_effect_corridor_between", "m4_between_count_control_pct", "m4_corridor_between_control_pct",
        "m4_geometric_corridor_effect", "m4_pseudo_corridor_pct", "m4_corridor_vs_sideband_control_ratio",
        "distance_link_score", "depth_penalty", "time_penalty", "stable_fraction",
        "raw_signal_level", "control_screen", "distance_plausibility_screen",
    ]
    return ordered_pairs(summary[keep_cols])



def build_concise_evidence_tables(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    evidence = ordered_pairs(data["pair_hypothesis_evidence_matrix"].copy())
    priority = ordered_pairs(data["followup_priority_table"].copy())
    next_steps = ordered_pairs(data["recommended_next_steps"].copy())

    concise = evidence.copy()
    concise["pair_label"] = concise["pair_name"].map(PAIR_LABELS)
    concise["hypothesis_label"] = concise["hypothesis"].map(HYPOTHESIS_LABELS)
    concise = concise[[
        "pair_name", "pair_label", "hypothesis", "hypothesis_label", "raw_score", "corrected_score", "distance_score",
        "raw_evidence", "control_corrected_evidence", "distance_aware_plausibility", "mechanism_context",
    ]]

    followup = concise.merge(priority, on=["pair_name", "hypothesis"], how="left", validate="one_to_one")
    require_columns(followup, ["followup_priority", "recommended_followup"], "followup_priorities_concise_intermediate")
    if followup[["followup_priority", "recommended_followup"]].isna().any().any():
        raise ValueError("Missing follow-up annotations after merging evidence and priority tables")
    followup = followup.merge(next_steps, on=["pair_name", "hypothesis", "followup_priority", "recommended_followup"], how="left", validate="one_to_one")
    followup["priority_num"] = followup["followup_priority"].map(PRIORITY_ORDER)
    followup = followup.sort_values(["priority_num", "corrected_score", "distance_score", "raw_score"], ascending=[False, False, False, False], kind="stable")
    followup = followup.drop(columns=["priority_num"])

    return {
        "relationship_evidence_matrix_concise": concise,
        "followup_priorities_concise": followup,
    }



def select_signal_tables(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    evidence = ordered_pairs(data["pair_hypothesis_evidence_matrix"].copy())
    priority = ordered_pairs(data["recommended_next_steps"].copy())
    merged = evidence.merge(priority, on=["pair_name", "hypothesis"], how="left", validate="one_to_one")
    require_columns(merged, ["followup_priority", "recommended_followup"], "signal_table_intermediate")
    if merged[["followup_priority", "recommended_followup"]].isna().any().any():
        raise ValueError("Missing follow-up annotations after merging evidence and next-step tables")
    merged["priority_num"] = merged["followup_priority"].map(PRIORITY_ORDER)
    merged["evidence_num"] = merged["control_corrected_evidence"].map(EVIDENCE_ORDER)
    merged["distance_num"] = merged["distance_aware_plausibility"].map(EVIDENCE_ORDER)
    merged["support_rank"] = merged["corrected_score"] + 0.5 * merged["distance_score"] + 0.25 * merged["raw_score"]

    strongest = merged[(merged["followup_priority"].isin(["high", "medium"])) & (merged["control_corrected_evidence"].isin(["strong", "moderate", "possible"]))].copy()
    strongest = strongest.sort_values(["priority_num", "support_rank", "distance_num", "evidence_num"], ascending=[False, False, False, False], kind="stable")
    strongest = strongest[[
        "pair_name", "hypothesis", "raw_score", "corrected_score", "distance_score", "raw_evidence",
        "control_corrected_evidence", "distance_aware_plausibility", "mechanism_context", "followup_priority", "recommended_followup",
    ]]

    weak = merged[(merged["control_corrected_evidence"] == "low") | (merged["distance_aware_plausibility"] == "low") | (merged["hypothesis"] == "apparent_relationship_from_background_or_window_choices")].copy()
    weak = weak.sort_values(["pair_name", "hypothesis"], kind="stable")
    weak = weak[[
        "pair_name", "hypothesis", "raw_score", "corrected_score", "distance_score", "raw_evidence",
        "control_corrected_evidence", "distance_aware_plausibility", "mechanism_context", "followup_priority", "recommended_followup",
    ]]
    return {
        "strongest_supported_signals": ordered_pairs(strongest),
        "weak_negative_unresolved_signals": ordered_pairs(weak),
        "recommended_next_steps_ranked": ordered_pairs(merged[["pair_name", "hypothesis", "followup_priority", "recommended_followup"]].drop_duplicates()),
    }



def evidence_sentence(row: pd.Series) -> str:
    hyp = HYPOTHESIS_LABELS.get(row["hypothesis"], row["hypothesis"])
    return (
        f"{hyp}: raw {row['raw_evidence']}, corrected {row['control_corrected_evidence']}, "
        f"distance-aware {row['distance_aware_plausibility']}, priority {row['followup_priority']}"
    )



def choose_pair_headlines(pair_name: str, evidence: pd.DataFrame) -> Dict[str, List[str]]:
    sub = evidence[evidence["pair_name"] == pair_name].copy()
    support = sub[sub["followup_priority"].isin(["high", "medium"])].copy()
    support = support.sort_values(["corrected_score", "distance_score", "raw_score"], ascending=[False, False, False], kind="stable")
    strong_lines = [evidence_sentence(row) for _, row in support.head(3).iterrows()]

    contradictions = sub[(sub["control_corrected_evidence"] == "low") | (sub["distance_aware_plausibility"] == "low")].copy()
    contradictions = contradictions.sort_values(["distance_score", "corrected_score", "raw_score"], ascending=[True, True, False], kind="stable")
    weak_lines = [evidence_sentence(row) for _, row in contradictions.head(3).iterrows()]
    return {"support": strong_lines, "weak": weak_lines}



def build_report_text(data: Dict[str, pd.DataFrame], pair_summary: pd.DataFrame, concise_evidence: pd.DataFrame, followup: pd.DataFrame, strong: pd.DataFrame, weak: pd.DataFrame) -> str:
    regional = data["regional_activation_summary"].copy()
    regional_map = dict(zip(regional["metric"], regional["value"]))
    lines: List[str] = []
    lines.append("# Final scientific report: M1-M2-M3 relationship synthesis")
    lines.append("")
    lines.append("## Scope")
    lines.append("This report assembles validated outputs from the relationship-analysis task without recomputing the core catalog metrics. Interpretations are catalog-level only and do not infer triggering or a physical mechanism from timing and proximity alone.")
    lines.append("")
    lines.append("## Executive summary")
    lines.append(f"- Catalog size: {int(regional_map.get('catalog_event_count', 0))} relocated events; M4+: {int(regional_map.get('m4plus_event_count', 0))}; M5+: {int(regional_map.get('m5plus_event_count', 0))}.")
    lines.append("- The pairwise synthesis does not support a single common story for all three cluster pairs.")
    lines.append("- M1-M3 is the clearest candidate for further physical verification because several relationship hypotheses remain at least moderate after controls and remain distance-plausible for nearby source regions.")
    lines.append("- M1-M2 shows strong raw and corrected evidence for broader regional activation, but its large separation and depth offset argue against a simple local pair-linkage interpretation.")
    lines.append("- M2-M3 is best treated primarily as independent local clusters embedded in a broader regional rate episode; local pair-linkage evidence is weak after distance-aware screening.")
    lines.append("- For all pairs, broader regional activation and common regional rate-pulse explanations remain important alternatives that must be separated from pair-specific linkage.")
    lines.append("")
    lines.append("## Pairwise relationship evidence summary")
    for row in pair_summary.itertuples(index=False):
        pair_name = row.pair_name
        headlines = choose_pair_headlines(pair_name, followup)
        lines.append(f"### {PAIR_LABELS[pair_name]}")
        m4_corridor_fraction_text = f"{row.m4_corridor_fraction:.3f}" if pd.notna(row.m4_corridor_fraction) else "nan"
        lines.append(f"- Raw catalog evidence: all-event between-mainshock count {int(row.n_between_mainshocks)}, corridor fraction {row.corridor_fraction:.3f}, ambiguous fraction {row.ambiguous_fraction:.3f}; M4+ between count {int(row.m4_between_count) if pd.notna(row.m4_between_count) else 0}, M4+ corridor fraction {m4_corridor_fraction_text}.")
        m4_between_pct_text = f"{row.m4_between_count_control_pct:.3f}" if pd.notna(row.m4_between_count_control_pct) else "nan"
        m4_pseudo_pct_text = f"{row.m4_pseudo_corridor_pct:.3f}" if pd.notna(row.m4_pseudo_corridor_pct) else "nan"
        m4_temporal_effect_text = f"{row.m4_temporal_effect_between:.1f}" if pd.notna(row.m4_temporal_effect_between) else "nan"
        m4_geometric_effect_text = f"{row.m4_geometric_corridor_effect:.1f}" if pd.notna(row.m4_geometric_corridor_effect) else "nan"
        lines.append(f"- Control-corrected evidence: M4+ temporal exceedance percentile {m4_between_pct_text}, M4+ geometric corridor percentile {m4_pseudo_pct_text}, M4+ temporal effect {m4_temporal_effect_text}, geometric corridor effect {m4_geometric_effect_text}; screening result = {row.control_screen}.")
        lines.append(f"- Distance-aware plausibility: separation {row.pair_sep_km:.1f} km, depth difference {row.pair_depth_diff_km:.1f} km, time separation {row.pair_time_sep_days:.1f} days, distance-link score {row.distance_link_score:.3f}; screen = {row.distance_plausibility_screen}.")
        if headlines["support"]:
            lines.append("- Strongest supported catalog-level signals:")
            for item in headlines["support"]:
                lines.append(f"  - {item}")
        if headlines["weak"]:
            lines.append("- Weak, contradictory, or unresolved signals:")
            for item in headlines["weak"]:
                lines.append(f"  - {item}")
        lines.append("")
    lines.append("## Relationship evidence matrix")
    lines.append("Evidence levels are reported separately for raw catalog evidence, control-corrected evidence, and distance-aware plausibility.")
    lines.append("")
    for pair in PAIR_ORDER:
        lines.append(f"### {PAIR_LABELS[pair]}")
        sub = concise_evidence[concise_evidence["pair_name"] == pair]
        for row in sub.itertuples(index=False):
            lines.append(
                f"- {row.hypothesis_label}: raw={row.raw_evidence}, corrected={row.control_corrected_evidence}, distance-aware={row.distance_aware_plausibility}."
            )
        lines.append("")
    lines.append("## Strongest supported relationship signals")
    for row in strong.head(12).itertuples(index=False):
        lines.append(
            f"- {PAIR_LABELS[row.pair_name]} — {HYPOTHESIS_LABELS[row.hypothesis]}: raw={row.raw_evidence}, corrected={row.control_corrected_evidence}, distance-aware={row.distance_aware_plausibility}, follow-up priority={row.followup_priority}."
        )
    lines.append("")
    lines.append("## Weak, negative, or unresolved evidence")
    for row in weak.head(15).itertuples(index=False):
        lines.append(
            f"- {PAIR_LABELS[row.pair_name]} — {HYPOTHESIS_LABELS[row.hypothesis]}: raw={row.raw_evidence}, corrected={row.control_corrected_evidence}, distance-aware={row.distance_aware_plausibility}, follow-up priority={row.followup_priority}."
        )
    lines.append("")
    lines.append("## Follow-up priorities")
    top_follow = followup[followup["followup_priority"] == "high"].copy()
    for row in top_follow.head(12).itertuples(index=False):
        lines.append(f"- {PAIR_LABELS[row.pair_name]} — {HYPOTHESIS_LABELS[row.hypothesis]}: {row.recommended_followup}.")
    lines.append("")
    lines.append("## Recommended next research directions")
    lines.append("- Prioritize M1-M3 for high-precision relocation, waveform cross-correlation, focal-mechanism comparison, and stress-screening because multiple pair-linkage hypotheses remain viable after controls and are geographically plausible at the catalog level.")
    lines.append("- Test M1-M2 and M2-M3 primarily as regional-episode or rate-pulse candidates using regional background-rate modeling, geodesy, ocean-bottom pressure, and stress-field context before investing in a simple pair-triggering narrative.")
    lines.append("- Use waveform-family analysis to distinguish swarm-like multi-event clustering from corridor-style migration, especially for M1-centered activity and any M1-M3 intervening chain candidates.")
    lines.append("- Revisit all pairwise interpretations after improved relocations and uncertainty-aware geometry checks, because distance-aware plausibility is a major filter on the raw relationship metrics.")
    lines.append("- Treat mechanism context only as a discriminator in follow-up work; current matched mechanism context is broadly compatible but not decisive from catalog evidence alone.")
    lines.append("")
    lines.append("## Bottom line")
    lines.append("The catalog most strongly supports further investigation of M1-M3 as a potentially meaningful nearby relationship and supports broader regional activation as an important framing hypothesis for all three clusters. M1-M2 and M2-M3 should not be prioritized as simple local pair-linkage cases based on catalog evidence alone, especially once control-corrected and distance-aware constraints are applied.")
    lines.append("")
    return "\n".join(lines)



def build_executive_summary(pair_summary: pd.DataFrame, strong: pd.DataFrame) -> str:
    lines = [
        "Aomori M1-M2-M3 relationship synthesis",
        "====================================",
        "",
        "Top scientific takeaways:",
        "- M1-M3 is the highest-priority pair for deeper physical follow-up.",
        "- M1-M2 and M2-M3 are better framed as regional-episode candidates than as simple local pair-linkages.",
        "- Broader regional activation remains a strong competing explanation across the system.",
        "",
        "Pair screens:",
    ]
    for row in pair_summary.itertuples(index=False):
        lines.append(
            f"- {PAIR_LABELS[row.pair_name]}: raw={row.raw_signal_level}, controls={row.control_screen}, distance={row.distance_plausibility_screen}."
        )
    lines.append("")
    lines.append("Highest-priority pair-hypothesis combinations:")
    for row in strong.head(8).itertuples(index=False):
        lines.append(
            f"- {PAIR_LABELS[row.pair_name]} — {HYPOTHESIS_LABELS[row.hypothesis]} ({row.followup_priority})"
        )
    lines.append("")
    lines.append("See final_scientific_report.md and companion CSV tables for the full evidence matrix.")
    return "\n".join(lines)



def copy_figures() -> pd.DataFrame:
    rows = []
    for fig_name in FIGURES_TO_COPY:
        src = ANALYSIS_DIR / fig_name
        require_file(src)
        dst = OUTPUT_DIR / fig_name
        shutil.copy2(src, dst)
        rows.append({"output_name": fig_name, "source": str(src), "category": "figure"})
        log(f"Copied figure: {src} -> {dst}")
    return pd.DataFrame(rows)



def write_outputs(outputs: Dict[str, pd.DataFrame], report_text: str, executive_summary: str, copied_manifest: pd.DataFrame) -> None:
    manifest_rows = []
    for name, df in outputs.items():
        path = OUTPUT_DIR / f"{name}.csv"
        df.to_csv(path, index=False)
        manifest_rows.append({"output_name": path.name, "category": "table", "rows": len(df)})
        log(f"Wrote table: {path} rows={len(df)}")
    report_path = OUTPUT_DIR / "final_scientific_report.md"
    report_path.write_text(report_text, encoding="utf-8")
    manifest_rows.append({"output_name": report_path.name, "category": "report", "rows": len(report_text.splitlines())})
    log(f"Wrote report: {report_path}")
    exec_path = OUTPUT_DIR / "executive_summary.txt"
    exec_path.write_text(executive_summary, encoding="utf-8")
    manifest_rows.append({"output_name": exec_path.name, "category": "summary", "rows": len(executive_summary.splitlines())})
    manifest = pd.concat([pd.DataFrame(manifest_rows), copied_manifest], ignore_index=True, sort=False)
    manifest.to_csv(OUTPUT_DIR / "report_manifest.csv", index=False)
    log(f"Wrote manifest: {OUTPUT_DIR / 'report_manifest.csv'}")



def main() -> None:
    ensure_output_dir()
    log(f"Reading validated relationship-analysis outputs from {ANALYSIS_DIR}")
    data = load_inputs()
    pair_summary = collect_pair_summary(data)
    concise_tables = build_concise_evidence_tables(data)
    signal_tables = select_signal_tables(data)
    report_text = build_report_text(
        data=data,
        pair_summary=pair_summary,
        concise_evidence=concise_tables["relationship_evidence_matrix_concise"],
        followup=concise_tables["followup_priorities_concise"],
        strong=signal_tables["strongest_supported_signals"],
        weak=signal_tables["weak_negative_unresolved_signals"],
    )
    executive_summary = build_executive_summary(pair_summary, signal_tables["strongest_supported_signals"])
    copied_manifest = copy_figures()
    outputs = {
        "pairwise_scientific_summary": pair_summary,
        "relationship_evidence_matrix_concise": concise_tables["relationship_evidence_matrix_concise"],
        "followup_priorities_concise": concise_tables["followup_priorities_concise"],
        "raw_corrected_distance_summary": pair_summary[[
            "pair_name", "pair_label", "raw_signal_level", "control_screen", "distance_plausibility_screen",
            "m4_between_count", "m4_corridor_fraction", "m4_ambiguous_fraction", "m4_between_count_control_pct",
            "m4_pseudo_corridor_pct", "pair_sep_km", "pair_depth_diff_km", "pair_time_sep_days", "distance_link_score",
        ]],
        "strongest_supported_signals": signal_tables["strongest_supported_signals"],
        "weak_negative_unresolved_signals": signal_tables["weak_negative_unresolved_signals"],
        "recommended_next_steps_ranked": signal_tables["recommended_next_steps_ranked"],
    }
    write_outputs(outputs, report_text, executive_summary, copied_manifest)
    log("Report synthesis complete")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        sys.exit(1)
