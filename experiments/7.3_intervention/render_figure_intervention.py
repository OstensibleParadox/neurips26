"""Render intervention certificate figures for S7.3.

Produces:
  1. Dormant vs active bar chart: JS divergence or loglik shift by task.
  2. Perturbation strength sweep: delta^LB vs perturbation sigma.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def render_dormant_active(results_path: str, out_path: str) -> None:
    """Bar chart comparing intervention delta^LB on dormant vs active tasks."""
    with open(results_path) as f:
        data = json.load(f)

    dormant_results = {k: v for k, v in data.items() if "calculator" in v.get("task", "")}
    active_results = {k: v for k, v in data.items() if "planning" in v.get("task", "")}

    fig, ax = plt.subplots(figsize=(6, 4))

    labels = []
    values = []
    errors = []
    colors = []

    for label_prefix, results in [("Dormant", dormant_results),
                                   ("Active", active_results)]:
        for key, result in results.items():
            js = result["js_divergence"]["js_divergence"]
            ci = result["js_divergence"]["ci_95"]
            labels.append(f"{label_prefix}\n{result['target']}")
            values.append(js)
            errors.append([js - ci[0], ci[1] - js])
            colors.append("#4CAF50" if label_prefix == "Dormant" else "#F44336")

    x = range(len(labels))
    err = np.array(errors).T
    ax.bar(x, values, yerr=err, color=colors, capsize=4, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7, rotation=0)
    ax.set_ylabel("JS(P_wild || P_perturbed)", fontsize=10)
    ax.axhline(y=0, color="gray", linewidth=0.5)
    ax.set_title("Intervention Certificate: Dormant vs Active", fontsize=11)

    # Add legend
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color="#4CAF50", label="Dormant (calculator)"),
        Patch(color="#F44336", label="Active (planning)"),
    ], fontsize=8)

    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def render_strength_sweep(results_dir: str, out_path: str) -> None:
    """Line chart: delta^LB vs perturbation strength sigma."""
    results_files = sorted(Path(results_dir).glob("intervention_*.json"))
    if not results_files:
        return

    all_data = {}
    for fpath in results_files:
        with open(fpath) as f:
            data = json.load(f)
        all_data.update(data)

    fig, ax = plt.subplots(figsize=(6, 4))

    # Group by target and extract strength->JS
    from collections import defaultdict
    sweeps = defaultdict(list)
    for key, result in all_data.items():
        pert = result.get("perturbation", {})
        mode = pert.get("mode", "")
        strength = pert.get("strength", 0)
        js = result["js_divergence"]["js_divergence"]
        target = result.get("target", "unknown")
        sweeps[target].append((strength, js))

    for target, points in sweeps.items():
        points.sort()
        strengths = [p[0] for p in points]
        jses = [p[1] for p in points]
        ax.plot(strengths, jses, "o-", label=target, linewidth=2, markersize=6)

    ax.set_xlabel("Perturbation strength σ", fontsize=10)
    ax.set_ylabel("JS(P_wild || P_perturbed)", fontsize=10)
    ax.set_title("Intervention Strength Sweep", fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd")

    da_p = sub.add_parser("dormant-active")
    da_p.add_argument("results", help="path to intervention results JSON")
    da_p.add_argument("--out", required=True)

    sw_p = sub.add_parser("strength-sweep")
    sw_p.add_argument("results_dir", help="directory with per-task intervention JSONs")
    sw_p.add_argument("--out", required=True)

    args = parser.parse_args()
    if args.cmd == "dormant-active":
        render_dormant_active(args.results, args.out)
    elif args.cmd == "strength-sweep":
        render_strength_sweep(args.results_dir, args.out)
