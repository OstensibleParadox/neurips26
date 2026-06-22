"""Render proxy certificate figures for S7.2."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def render_proxy_ablation(ablation_json: str, out_path: str) -> None:
    with open(ablation_json) as f:
        data = json.load(f)

    details = data["details"]
    levels = ["random", "d1", "d3", "d5", "full"]
    labels = ["random", "d=1 PCA", "d=3 PCA", "d=5 PCA", "full (10-dim)"]
    ln2 = np.log(2)

    values = []
    errors_lo = []
    errors_hi = []
    for level in levels:
        d = details[level]
        bits = d["delta_act_lb_nats"] / ln2
        ci = [c / ln2 for c in d["ci_95"]]
        values.append(bits)
        errors_lo.append(bits - ci[0])
        errors_hi.append(ci[1] - bits)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = np.arange(len(labels))
    err = [errors_lo, errors_hi]
    colors = ["#999" if l == "random" else "#2196F3" for l in levels]
    bars = ax.bar(x, values, yerr=err, color=colors, capsize=4, width=0.55)

    ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=15, ha="right")
    ax.set_ylabel(r"$\delta_{act}^{LB}$ (bits)", fontsize=10)

    # Annotate values
    for i, (v, bar) in enumerate(zip(values, bars)):
        ax.annotate(f"{v:+.4f}", (bar.get_x() + bar.get_width()/2, v),
                    textcoords="offset points", xytext=(0, 8 if v >= 0 else -14),
                    ha="center", fontsize=7.5)

    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ablation_json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    render_proxy_ablation(args.ablation_json, args.out)
