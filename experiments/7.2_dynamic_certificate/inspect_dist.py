"""Quick diagnostic: load probe pairs, plot Z distribution, Z_0 vs Z_1 by action.

Usage:
  python inspect_dist.py --pairs data/processed/probe_pairs.pt
  python inspect_dist.py --pairs data/processed/probe_pairs_planning.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch


def inspect(pairs_path: str, out_path: str = "z_distribution.png") -> None:
    pairs = torch.load(pairs_path, map_location="cpu")
    Z = pairs[:, :-1]
    A = pairs[:, -1]

    print(f"Z shape: {Z.shape}")
    print(f"Z mean: {Z.mean().item():.4f}, std: {Z.std().item():.4f}")
    print(f"A values: {np.unique(A.numpy())}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.hist(Z.flatten().numpy(), bins=50)
    ax1.set_title("Z distribution")

    ax2.scatter(Z[:, 0].numpy(), Z[:, 1].numpy(), c=A.numpy(), cmap='viridis', alpha=0.5)
    ax2.set_title("Z_0 vs Z_1 colored by Action")

    fig.tight_layout()
    fig.savefig(out_path)
    print(f"Saved visualization to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True,
                        help="Path to probe pairs .pt file")
    parser.add_argument("--out", default="z_distribution.png",
                        help="Output image path")
    args = parser.parse_args()
    inspect(args.pairs, args.out)
