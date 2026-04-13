"""Rho-sweep plot for the representation-near sensitivity family (Def. 8).

Reads cached per-pair metrics (no LM scoring), sweeps rho over a grid,
computes V_g(rho, tau_j) with per-judge tau AND M_g(rho)/tau_j with
cluster-bootstrap 95% CIs. Output: paper/figures/cfsg_rho_sweep.pdf.
Used by main.tex Section 6.1 as the main-text curve companion to Table 1.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src.metrics.cfsg_metrics import (  # noqa: E402
    pairwise_violation_rate,
    violation_rate,
)
from src.utils.bootstrap import cluster_bootstrap_fn  # noqa: E402

DATA = REPO / "data" / "compiled"
UNIFIED = DATA / "cfsg_unified_metrics.csv"
PAIRWISE = DATA / "cfsg_pairwise_metrics.csv"
THRESH = DATA / "cfsg_threshold_report.json"
OUT = REPO / "paper" / "figures" / "cfsg_rho_sweep.pdf"

JUDGE_LABELS = {
    "armo": "ArmoRM",
    "skywork": "Skywork",
    "api-sonnet": "Claude Sonnet",
    "pairrm": "PairRM",
}
JUDGE_COLORS = {
    "armo": "#1f77b4",
    "skywork": "#2ca02c",
    "api-sonnet": "#ff7f0e",
    "pairrm": "#d62728",
}

N_BOOT = 1000
RHO_GRID = np.linspace(0.04, 0.20, 20)


def load_unified() -> list[dict]:
    out = []
    with UNIFIED.open() as f:
        for r in csv.DictReader(f):
            try:
                d = float(r["d_repr"])
                dg = float(r["delta_g"])
            except (ValueError, KeyError):
                continue
            if np.isnan(d) or np.isnan(dg):
                continue
            out.append(
                {
                    "judge": r["judge"],
                    "mode": r["mode"].lower(),
                    "content_id": r["content_id"],
                    "d_repr": d,
                    "delta_g": dg,
                }
            )
    return out


def load_pairwise() -> list[dict]:
    out = []
    with PAIRWISE.open() as f:
        for r in csv.DictReader(f):
            try:
                d = float(r["d_repr"])
                p = float(r["p_ij"])
            except (ValueError, KeyError):
                continue
            if np.isnan(d) or np.isnan(p):
                continue
            out.append(
                {
                    "mode": r["mode"].lower(),
                    "content_id": r["content_id"],
                    "d_repr": d,
                    "p_ij": p,
                }
            )
    return out


def conditional_mean(deltas: np.ndarray, d_reprs: np.ndarray, rho: float) -> float:
    mask = d_reprs <= rho
    if mask.sum() == 0:
        return float("nan")
    return float(deltas[mask].mean())


def sweep_pointwise(
    rows: list[dict], judge: str, tau: float, rho_grid: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sub = [r for r in rows if r["judge"] == judge]
    deltas = np.array([r["delta_g"] for r in sub])
    d_reprs = np.array([r["d_repr"] for r in sub])
    cids = np.array([r["content_id"] for r in sub])

    v_pt = np.zeros(len(rho_grid))
    v_lo = np.zeros(len(rho_grid))
    v_hi = np.zeros(len(rho_grid))
    m_pt = np.zeros(len(rho_grid))
    m_lo = np.zeros(len(rho_grid))
    m_hi = np.zeros(len(rho_grid))

    for i, rho in enumerate(rho_grid):

        def vr_fn(d, r, rho=rho, tau=tau):
            return violation_rate(d, r, rho, tau)

        def mg_fn(d, r, rho=rho):
            return conditional_mean(d, r, rho)

        v_pt[i], v_lo[i], v_hi[i] = cluster_bootstrap_fn(
            vr_fn, [deltas, d_reprs], cids, n=N_BOOT
        )
        m_pt[i], m_lo[i], m_hi[i] = cluster_bootstrap_fn(
            mg_fn, [deltas, d_reprs], cids, n=N_BOOT
        )

    return v_pt, v_lo, v_hi, m_pt, m_lo, m_hi


def sweep_pairwise(
    pair_rows: list[dict], gamma: float, rho_grid: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    p_ijs = np.array([r["p_ij"] for r in pair_rows])
    d_reprs = np.array([r["d_repr"] for r in pair_rows])
    cids = np.array([r["content_id"] for r in pair_rows])

    w_pt = np.zeros(len(rho_grid))
    w_lo = np.zeros(len(rho_grid))
    w_hi = np.zeros(len(rho_grid))

    for i, rho in enumerate(rho_grid):

        def w_fn(p, d, rho=rho, gamma=gamma):
            return pairwise_violation_rate(p, d, rho, gamma)

        w_pt[i], w_lo[i], w_hi[i] = cluster_bootstrap_fn(
            w_fn, [p_ijs, d_reprs], cids, n=N_BOOT
        )

    return w_pt, w_lo, w_hi


def main() -> None:
    np.random.seed(42)

    thresh = json.loads(THRESH.read_text())
    tau_per_judge = thresh["per_judge_tau"]
    gamma = float(thresh.get("gamma", 0.1))
    rho_marker = float(thresh.get("rho_p25", 0.0744))

    rows_all = load_unified()
    pair_all = load_pairwise()

    rows_b = [r for r in rows_all if r["mode"] == "b"]
    pair_b = [r for r in pair_all if r["mode"] == "b"]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    ax_v, ax_m = axes

    judges = ["armo", "skywork", "api-sonnet"]
    for judge in judges:
        tau = float(tau_per_judge[judge])
        v_pt, v_lo, v_hi, m_pt, m_lo, m_hi = sweep_pointwise(
            rows_b, judge, tau, RHO_GRID
        )
        color = JUDGE_COLORS[judge]
        label = JUDGE_LABELS[judge]

        ax_v.plot(RHO_GRID, v_pt, color=color, label=label, linewidth=1.8)
        ax_v.fill_between(RHO_GRID, v_lo, v_hi, color=color, alpha=0.18)

        m_pt_norm = m_pt / tau
        m_lo_norm = m_lo / tau
        m_hi_norm = m_hi / tau
        ax_m.plot(RHO_GRID, m_pt_norm, color=color, label=label, linewidth=1.8)
        ax_m.fill_between(RHO_GRID, m_lo_norm, m_hi_norm, color=color, alpha=0.18)

    w_pt, w_lo, w_hi = sweep_pairwise(pair_b, gamma, RHO_GRID)
    ax_v.plot(
        RHO_GRID,
        w_pt,
        color=JUDGE_COLORS["pairrm"],
        label=f"PairRM  $W(\\rho,\\gamma)$",
        linewidth=1.8,
        linestyle="--",
    )
    ax_v.fill_between(
        RHO_GRID, w_lo, w_hi, color=JUDGE_COLORS["pairrm"], alpha=0.12
    )

    for ax in axes:
        ax.axvline(rho_marker, color="gray", linestyle=":", linewidth=1.0, alpha=0.7)
        ax.grid(alpha=0.3)
        ax.set_xlabel(r"$\rho$ (representation distance threshold)", fontsize=10)

    ax_v.set_ylabel(r"$V_g(\rho,\tau_j)$  /  $W(\rho,\gamma)$", fontsize=10)
    ax_v.set_title("Conditional violation rate", fontsize=11)
    ax_v.set_ylim(-0.02, 1.02)
    ax_v.legend(fontsize=8, loc="best")

    ax_m.set_ylabel(
        r"$M_g(\rho)/\tau_j = \mathbb{E}[|\Delta R|\mid d\leq \rho]/\tau_j$",
        fontsize=10,
    )
    ax_m.set_title("Conditional mean gap (normalized)", fontsize=11)
    ax_m.legend(fontsize=8, loc="best")

    fig.suptitle(
        r"Representation-near sensitivity family across the small-distance regime (Mode B)",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
