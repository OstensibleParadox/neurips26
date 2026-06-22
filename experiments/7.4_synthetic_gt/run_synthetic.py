r"""Synthetic ground-truth for S7.4: controlled hidden influence.

Generates agent data with known I(H; A_t | ~T_t). A binary hidden variable H
shifts the action logits by a controlled amount.  The true conditional MI is
computed via Monte Carlo integration over the known generative model.

Static bound: H is an unlogged binary channel, capacity = 1 bit.
Dynamic bound: CE-diff estimator with 5-fold cross-validation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Import v3 estimator
try:
    from .synthetic_v3_estimator import run_v3_estimation
except ImportError:
    # Handle relative import issue when running as script
    import sys
    sys.path.append(str(Path(__file__).parent))
    from synthetic_v3_estimator import run_v3_estimation


def generate_data(n=1000, d_tilde=8, n_classes=5, beta_h=0.0, seed=42):
    """Generate synthetic data with controlled hidden influence.

    P(A = k | T, H) = softmax(T @ W_k + beta_h * H * delta_{k,0})

    beta_h=0 -> H has no influence -> I(H;A|T)=0
    Larger beta_h -> stronger influence -> higher conditional MI.
    """
    rng = np.random.RandomState(seed)
    T = rng.randn(n, d_tilde).astype(np.float32)
    H = (rng.rand(n) > 0.5).astype(np.float32)
    W = rng.randn(d_tilde, n_classes).astype(np.float32) * 0.5

    logits = T @ W
    # H pushes toward class 0
    bias = np.zeros((n, n_classes), dtype=np.float32)
    bias[:, 0] = beta_h * H
    logits = logits + bias + rng.randn(n, n_classes).astype(np.float32) * 0.1

    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs /= probs.sum(axis=1, keepdims=True)
    A = np.array([rng.choice(n_classes, p=p) for p in probs])

    # Monte Carlo estimate of true I(H; A | T)
    # I(H;A|T) = E_{T,H,A}[log P(A|T,H) - log P(A|T)]
    # P(A|T) = sum_h P(H=h) * P(A|T,H=h)
    true_mi = _mc_mi(T, H, A, W, beta_h, n_classes)

    return T, H, A, probs, true_mi


def _mc_mi(T, H, A, W, beta_h, n_classes):
    """Monte Carlo estimate of I(H; A | T)."""
    n = len(T)
    # P(A|T,H): already have from generative model
    # P(A|T): marginalize over H ~ Bern(0.5)
    logits_T = T @ W
    # H=0 case
    logits_h0 = logits_T + np.random.RandomState(0).randn(n, n_classes).astype(np.float32) * 0
    probs_h0 = np.exp(logits_h0 - logits_h0.max(axis=1, keepdims=True))
    probs_h0 /= probs_h0.sum(axis=1, keepdims=True)
    # H=1 case (push toward class 0)
    bias = np.zeros((n, n_classes), dtype=np.float32)
    bias[:, 0] = beta_h
    logits_h1 = logits_T + bias
    probs_h1 = np.exp(logits_h1 - logits_h1.max(axis=1, keepdims=True))
    probs_h1 /= probs_h1.sum(axis=1, keepdims=True)

    # Marginal: 0.5 * P(A|T,H=0) + 0.5 * P(A|T,H=1)
    probs_marginal = 0.5 * probs_h0 + 0.5 * probs_h1

    # I(H;A|T) = sum_{h,a} P(h) * P(a|T,h) * log(P(a|T,h) / P(a|T))
    mi_sum = 0.0
    for i in range(n):
        a = A[i]
        h = H[i]
        if h == 0:
            p_cond = probs_h0[i, a]
        else:
            p_cond = probs_h1[i, a]
        p_marg = probs_marginal[i, a]
        if p_cond > 0 and p_marg > 0:
            mi_sum += np.log(p_cond / p_marg)
    return mi_sum / n


def ce_diff_estimate(T, H, A, n_classes, n_folds=5):
    """Cross-validated CE-diff: I_hat = L(T) - L(T,H)."""
    n = len(A)
    indices = np.arange(n)
    rng = np.random.RandomState(42)
    rng.shuffle(indices)
    fold_size = n // n_folds

    ce_diffs = []
    for fold in range(n_folds):
        test_idx = indices[fold * fold_size:(fold + 1) * fold_size]
        train_idx = np.setdiff1d(indices, test_idx)

        # Trace-only
        m_t = nn.Sequential(nn.Linear(T.shape[1], 16), nn.ReLU(), nn.Linear(16, n_classes))
        opt = optim.Adam(m_t.parameters(), lr=0.01)
        crit = nn.CrossEntropyLoss()
        Xt = torch.FloatTensor(T[train_idx])
        yt = torch.LongTensor(A[train_idx])
        for _ in range(300):
            opt.zero_grad()
            crit(m_t(Xt), yt).backward()
            opt.step()
        with torch.no_grad():
            ce_t = crit(m_t(torch.FloatTensor(T[test_idx])), torch.LongTensor(A[test_idx])).item()

        # Trace + H
        Xp_train = np.column_stack([T[train_idx], H[train_idx]])
        Xp_test = np.column_stack([T[test_idx], H[test_idx]])
        m_p = nn.Sequential(nn.Linear(Xp_train.shape[1], 16), nn.ReLU(), nn.Linear(16, n_classes))
        opt2 = optim.Adam(m_p.parameters(), lr=0.01)
        Xpt = torch.FloatTensor(Xp_train)
        for _ in range(300):
            opt2.zero_grad()
            crit(m_p(Xpt), yt).backward()
            opt2.step()
        with torch.no_grad():
            ce_p = crit(m_p(torch.FloatTensor(Xp_test)), torch.LongTensor(A[test_idx])).item()

        ce_diffs.append(ce_t - ce_p)

    return float(np.mean(ce_diffs)), float(np.std(ce_diffs) / np.sqrt(n_folds))


def ce_diff_estimate_v3(T, H, A, seed=42):
    """V3 CE-diff estimator using hardened pipeline from synthetic_v3_estimator.py."""
    # Semantic mapping: T→Phi, H→Z, A→A_in
    Phi_raw = T.astype(np.float32)
    Z_raw = H.reshape(-1, 1).astype(np.float32)  # Make H a column vector
    A_in = A.astype(int)

    # For synthetic data with no task structure, use singleton groups
    task_ids = np.arange(len(A))

    # Run v3 estimation
    result = run_v3_estimation(Phi_raw, Z_raw, A_in, task_ids, rng_seed=seed)

    return result


def main(n_trajectories: int = 1000,
         beta_levels: list[float] | None = None,
         out_dir: str = "data/processed/synthetic",
         skip_plot: bool = False,
         estimator: str = "legacy"):
    if beta_levels is None:
        beta_levels = [0.0, 0.5, 1.0, 2.0, 4.0]
    results = []

    print(f"Running with {estimator} estimator...")

    for beta_h in beta_levels:
        T, H, A, probs, true_mi = generate_data(n=n_trajectories, beta_h=beta_h)
        true_mi_bits = true_mi / np.log(2)

        if estimator == "legacy":
            delta_nats, delta_se = ce_diff_estimate(T, H, A, 5)
            delta_bits = delta_nats / np.log(2)

            results.append({
                "beta_h": float(beta_h),
                "true_mi_nats": float(true_mi),
                "true_mi_bits": float(true_mi_bits),
                "true_H_bits": 1.0,
                "epsilon_ub_bits": 1.0,
                "delta_lb_nats": float(delta_nats),
                "delta_lb_bits": float(delta_bits),
                "delta_se": float(delta_se),
            })
            bound_ok = "OK" if delta_bits <= true_mi_bits else "VIOLATION"
            print(f"  beta={beta_h:.1f}: true_MI={true_mi_bits:.4f} bits, "
                  f"delta^LB={delta_bits:.4f} bits, eps^UB=1.0 bits [{bound_ok}]")

        elif estimator == "v3":
            v3_result = ce_diff_estimate_v3(T, H, A)
            raw_gap_bits = v3_result["raw_gap_bits"]
            null_p95_bits = v3_result["null_p95_bits"]
            null_corrected_gap_bits = v3_result["null_corrected_gap_bits"]
            certified_delta_LB_bits = v3_result["certified_delta_LB_bits"]
            null_pass = v3_result["null_pass"]

            results.append({
                "beta_h": float(beta_h),
                "true_mi_nats": float(true_mi),
                "true_mi_bits": float(true_mi_bits),
                "raw_gap_bits": float(raw_gap_bits),
                "null_p95_bits": float(null_p95_bits),
                "null_corrected_gap_bits": float(null_corrected_gap_bits),
                "certified_delta_LB_bits": float(certified_delta_LB_bits) if certified_delta_LB_bits is not None else None,
                "null_pass": bool(null_pass),
                "n": int(n_trajectories),
                "n_null_repeats": int(v3_result["n_null_repeats"]),
                "n_classes": int(5), # n_classes is always 5 for this synthetic data
                "task_grouping": str(v3_result["task_grouping"])
            })

            status = "OK" if null_pass else "INVALID"
            cert_str = f"{certified_delta_LB_bits:.4f}" if certified_delta_LB_bits is not None else "None"
            print(f"  beta={beta_h:.1f}: true_MI={true_mi_bits:.4f} bits, "
                  f"raw_gap={raw_gap_bits:.4f} bits, null_p95={null_p95_bits:.4f} bits, "
                  f"cert_delta_LB={cert_str} bits [{status}]")

        else:
            raise ValueError(f"Unknown estimator: {estimator}")

    # Choose output file based on estimator
    if estimator == "legacy":
        out_file = "synthetic_results.json"
    else:
        out_file = "synthetic_results_v3.json"

    out = Path(out_dir) / out_file
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out}")

    # Generate figure (only for legacy for now)
    if not skip_plot and estimator == "legacy":
        _plot(results, out_dir)
    return results


def _plot(results, out_dir: str = "data/processed/synthetic"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    true_mi = [r["true_mi_bits"] for r in results]
    delta_lb = [max(0, r["delta_lb_bits"]) for r in results]
    eps_ub = [r["epsilon_ub_bits"] for r in results]
    true_h = [r["true_H_bits"] for r in results]

    fig, ax = plt.subplots(figsize=(6, 4))
    x = range(len(results))
    ax.plot(x, eps_ub, "s-", color="#2196F3", label=r"$\varepsilon_{state}^{UB}$", linewidth=2)
    ax.plot(x, true_h, "o--", color="#2196F3", alpha=0.5, label=r"true $H(S_t|\tilde T_t)$")
    ax.plot(x, true_mi, "o-", color="#333", label=r"true $I(S_t;A_t|\tilde T_t)$", linewidth=2)
    ax.plot(x, delta_lb, "^--", color="#F44336", label=r"$\delta_{act}^{LB}$", linewidth=2)

    ax.fill_between(x, eps_ub, true_h, alpha=0.1, color="#2196F3")
    ax.fill_between(x, true_mi, delta_lb, alpha=0.1, color="#F44336")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{r['beta_h']:g}" for r in results])
    ax.set_xlabel(r"Hidden influence strength $\beta_h$", fontsize=10)
    ax.set_ylabel("Bits", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)

    out = Path(out_dir) / "synthetic_gt.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Figure saved to {out}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Synthetic ground-truth validation for dual certificates.")
    parser.add_argument("--n-trajectories", type=int, default=1000,
                        help="Number of trajectories per beta level (default: 1000)")
    parser.add_argument("--beta-levels", type=float, nargs="+",
                        default=[0.0, 0.5, 1.0, 2.0, 4.0],
                        help="Hidden influence strengths (default: 0.0 0.5 1.0 2.0 4.0)")
    parser.add_argument("--out-dir", default="data/processed/synthetic",
                        help="Output directory for results (default: data/processed/synthetic)")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip figure generation")
    parser.add_argument("--estimator", choices=["legacy", "v3"], default="legacy",
                        help="Estimator to use: legacy (original neural net) or v3 (hardened pipeline)")
    args = parser.parse_args()
    main(n_trajectories=args.n_trajectories, beta_levels=args.beta_levels,
         out_dir=args.out_dir, skip_plot=args.no_plot, estimator=args.estimator)
