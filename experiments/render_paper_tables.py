"""Render paper tables and headline macros from checked-in processed outputs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "processed"
DEFAULT_OUT_DIR = ROOT / "paper" / "tables"


TASK_LABELS = {
    "calculator_only": "Calculator (dormant)",
    "planning_search": "Planning (active)",
}

MULTI_AGENT_LABELS = {
    "neutral_replay": "Neutral replay",
    "counterfactual_evidence": "Counterfactual evidence",
    "same_class_shuffle": "Same-class shuffle",
    "oracle_tag_upper_bound": "Oracle tag upper-bound",
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def bits_from_intervention(row: dict) -> float:
    if "js_divergence_bits" in row:
        return float(row["js_divergence_bits"])
    return float(row["js_divergence"]) / math.log(2)


def ci_bits_from_intervention(row: dict) -> list[float]:
    if "js_ci_95_bits" in row:
        return [float(x) for x in row["js_ci_95_bits"]]
    return [float(x) / math.log(2) for x in row["js_ci_95"]]


def fmt(value: float, digits: int) -> str:
    if abs(value) < 0.5 * 10 ** (-digits):
        return "0" if digits == 0 else f"{0:.{digits}f}"
    return f"{value:.{digits}f}"


def fmt_ci(values: list[float], digits: int, *, tex_space: bool = False) -> str:
    lo, hi = values
    if abs(lo) < 1e-12 and abs(hi) < 1e-12:
        return "[0,0]"
    sep = ",\\ " if tex_space else ","
    return f"[{fmt(lo, digits)}{sep}{fmt(hi, digits)}]"


def intervention_row(data: dict, task: str, mode: str, strength: float) -> dict:
    key = f"{task}/scratchpad/{mode}/{strength:.1f}"
    if key not in data:
        raise KeyError(f"missing intervention row {key}")
    return data[key]


def render_intervention_table(data_dir: Path, out_dir: Path) -> None:
    dormant = load_json(data_dir / "intervention" / "intervention_calculator_only.json")
    active = load_json(data_dir / "intervention" / "intervention_planning_search.json")
    rows = [
        ("calculator_only", "mask", 0.7, intervention_row(dormant, "calculator_only", "mask", 0.7)),
        ("planning_search", "mask", 0.7, intervention_row(active, "planning_search", "mask", 0.7)),
        ("calculator_only", "replace", 1.0, intervention_row(dormant, "calculator_only", "replace", 1.0)),
        ("planning_search", "replace", 1.0, intervention_row(active, "planning_search", "replace", 1.0)),
    ]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\begin{tabular}{llcc}",
        "\\toprule",
        "Task & Perturbation & JS (bits; nats) & 95\\% CI (bits) \\\\",
        "\\midrule",
    ]
    for task, mode, strength, row in rows:
        bits = bits_from_intervention(row)
        nats = float(row["js_divergence"])
        ci = ci_bits_from_intervention(row)
        lines.append(
            f"{TASK_LABELS[task]} & {mode} ${strength:.1f}$ & "
            f"${fmt(bits, 4)}$; ${fmt(nats, 4)}$ & ${fmt_ci(ci, 4)}$ \\\\"
        )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\caption{Dynamic intervention certificate under the same unlogged-scratchpad",
        "topology. Dormant calculator tasks show no detectable scratchpad influence;",
        "active planning tasks show positive action-distribution shift.}",
        "\\label{tab:intervention-results}",
        "\\end{table}",
    ]
    (out_dir / "react_intervention_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_replay_table(data_dir: Path, out_dir: Path) -> None:
    summary_path = data_dir / "intervention" / "react_replay_summary.csv"
    if summary_path.exists():
        rows = load_csv_rows(summary_path)
    else:
        replay = load_json(data_dir / "intervention" / "replay_certificate.json")
        rows = []
        for split, task in [("dormant", "calculator_only"), ("active", "planning_search")]:
            row = replay[split]["replay_empty"]
            rows.append({
                "task": task,
                "task_label": TASK_LABELS[task],
                "replay_condition": "scratchpad removed",
                "js_bits": str(row["js_divergence_bits"]),
                "js_nats": str(row["js_divergence_nats"]),
                "ci_low_bits": str(row["ci_95_bits"][0]),
                "ci_high_bits": str(row["ci_95_bits"][1]),
                "argmax_tool_counts_unchanged": str(row.get("argmax_tool_counts_unchanged", "")).lower(),
            })
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\small",
        "\\begin{tabular}{llccc}",
        "\\toprule",
        "Task & Replay & JS (bits; nats) & 95\\% CI & Argmax \\\\",
        "\\midrule",
    ]
    for row in rows:
        unchanged = str(row.get("argmax_tool_counts_unchanged", "")).lower() == "true"
        argmax_text = "same" if unchanged else "changed"
        task_label = row.get("task_label") or TASK_LABELS[row["task"]]
        task_label = task_label.replace("Calculator", "Calc.")
        replay_condition = row["replay_condition"].replace("scratchpad ", "")
        lines.append(
            f"{task_label} & {replay_condition} & "
            f"${fmt(float(row['js_bits']), 4)}$; "
            f"${fmt(float(row['js_nats']), 4)}$ & "
            f"${fmt_ci([float(row['ci_low_bits']), float(row['ci_high_bits'])], 4)}$ & "
            f"{argmax_text} \\\\"
        )
    all_unchanged = all(
        str(row.get("argmax_tool_counts_unchanged", "")).lower() == "true"
        for row in rows
    )
    argmax_sentence = (
        "In both rows, aggregate argmax tool counts are unchanged."
        if all_unchanged
        else "The argmax-count column marks whether aggregate tool counts changed."
    )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\caption{Controlled replay certificate over soft tool-token probability",
        "distributions. Wild episodes use the full hidden scratchpad; replay episodes",
        "use the same visible trace with the scratchpad removed. The dormant-to-active",
        f"contrast mirrors the intervention result at the soft-policy level. {argmax_sentence}" + "}",
        "\\label{tab:replay-results}",
        "\\end{table}",
    ]
    (out_dir / "react_replay_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_multi_agent_table(data_dir: Path, out_dir: Path) -> None:
    summary = load_json(data_dir / "multi_agent_certificate" / "summary.json")
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        "Condition & $\\delta_\\text{act}^\\text{LB}$ (JS bits) & 95\\% CI (bits) \\\\",
        "\\midrule",
    ]
    for key, label in MULTI_AGENT_LABELS.items():
        row = summary["contrasts"][key]
        ci = [float(x) for x in row["ci_95_bits"]]
        lines.append(
            f"{label} & ${fmt(float(row['mean_js_bits']), 3)}$ & "
            f"${fmt_ci(ci, 3, tex_space=True)}$ \\\\"
        )
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\caption{Topological activation profile for the multi-agent deployment.",
        "Counterfactual evidence nearly saturates the binary action ceiling, while",
        "same-class shuffling remains much smaller. Hidden communication is therefore",
        "behaviorally active when the controller has delegated evidence gathering to",
        "the worker.}",
        "\\label{tab:multi-agent-dynamic}",
        "\\end{table}",
    ]
    (out_dir / "multi_agent_dynamic.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_headline_macros(data_dir: Path, out_dir: Path) -> None:
    replay = load_json(data_dir / "intervention" / "replay_certificate.json")
    intervention = load_json(data_dir / "intervention" / "intervention_planning_search.json")
    llada = load_json(data_dir / "diffusion_certificate" / "llada_temporal_k10.json")
    multi = load_json(data_dir / "multi_agent_certificate" / "summary.json")

    replay_row = replay["active"]["replay_empty"]
    mask_row = intervention_row(intervention, "planning_search", "mask", 0.7)
    llada_target = llada["results"]["step_10_target_gaussian_5"]
    llada_control = llada["results"]["step_10_control_gaussian_5"]
    multi_counterfactual = multi["contrasts"]["counterfactual_evidence"]

    lines = [
        "% Generated by experiments/render_paper_tables.py.",
        f"\\newcommand{{\\ReactReplayBits}}{{{fmt(float(replay_row['js_divergence_bits']), 4)}}}",
        f"\\newcommand{{\\ReactReplayCI}}{{{fmt_ci([float(x) for x in replay_row['ci_95_bits']], 4)}}}",
        f"\\newcommand{{\\ReactInterventionMaskBits}}{{{fmt(bits_from_intervention(mask_row), 4)}}}",
        f"\\newcommand{{\\ReactInterventionMaskCI}}{{{fmt_ci(ci_bits_from_intervention(mask_row), 4)}}}",
        f"\\newcommand{{\\LladaFinalBits}}{{{fmt(float(llada_target['js_divergence_bits']), 3)}}}",
        f"\\newcommand{{\\LladaFinalCI}}{{{fmt_ci([float(x) for x in llada_target['ci_95_bits']], 3)}}}",
        f"\\newcommand{{\\LladaControlFinalBits}}{{{fmt(float(llada_control['js_divergence_bits']), 3)}}}",
        f"\\newcommand{{\\LladaControlFinalCI}}{{{fmt_ci([float(x) for x in llada_control['ci_95_bits']], 3)}}}",
        f"\\newcommand{{\\MultiAgentCounterfactualBits}}{{{fmt(float(multi_counterfactual['mean_js_bits']), 3)}}}",
        f"\\newcommand{{\\MultiAgentCounterfactualCI}}{{{fmt_ci([float(x) for x in multi_counterfactual['ci_95_bits']], 3)}}}",
    ]
    (out_dir / "dynamic_headline_macros.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    render_intervention_table(args.data_dir, args.out_dir)
    render_replay_table(args.data_dir, args.out_dir)
    render_multi_agent_table(args.data_dir, args.out_dir)
    render_headline_macros(args.data_dir, args.out_dir)
    print(f"wrote generated tables to {args.out_dir}")


if __name__ == "__main__":
    main()
