"""Render LLaDA temporal certificate figure for S6.6."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def render_temporal(data_json: str, out_path: str) -> None:
    with open(data_json) as f:
        data = json.load(f)

    results = data["results"]
    steps = [2, 4, 6, 8, 10]

    def get_series(layer_type: str):
        vals, los, his = [], [], []
        for s in steps:
            key = f"step_{s}_{layer_type}_gaussian_5"
            r = results[key]
            vals.append(r["js_divergence_bits"])
            ci = r["ci_95_bits"]
            los.append(r["js_divergence_bits"] - ci[0])
            his.append(ci[1] - r["js_divergence_bits"])
        return vals, los, his

    target_vals, target_lo, target_hi = get_series("target")
    control_vals, control_lo, control_hi = get_series("control")

    fig, ax = plt.subplots(figsize=(7, 3.8))

    x = np.arange(len(steps))
    width = 0.3

    ax.bar(x - width / 2, target_vals, width, yerr=[target_lo, target_hi],
           capsize=4, color="#2196F3", label="Target layer (layer 1)")
    ax.bar(x + width / 2, control_vals, width, yerr=[control_lo, control_hi],
           capsize=4, color="#9E9E9E", label="Control layer (layer 31)")

    ax.set_xticks(x)
    ax.set_xticklabels([f"Step {s}" for s in steps])
    ax.set_ylabel(r"$\delta_{\mathrm{act}}^{\mathrm{LB}}$ (JS bits)")
    ax.set_xlabel("Denoising step")
    ax.legend(loc="upper left", frameon=True)
    ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="--")
    ax.set_ylim(bottom=-0.01)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/processed/diffusion_certificate/llada_temporal_k10.json")
    parser.add_argument("--out", default="paper/figures/llada_temporal.pdf")
    args = parser.parse_args()
    render_temporal(args.data, args.out)
