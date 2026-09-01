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


DEFAULT_NOISE_STD = 0.1
DEFAULT_GT_INNER_SAMPLES = 4096
DEFAULT_GT_SEED = 314159
DEFAULT_GT_BATCH_SIZE = 64

_MECHANISM_STREAM = 101
_DATA_STREAM = 211
_ACTION_STREAM = 307
_GROUND_TRUTH_STREAM = 401


def _make_rng(seed: int, stream: int) -> np.random.Generator:
    """Create a deterministic RNG stream without coupling independent roles."""
    if seed < 0:
        raise ValueError("seeds must be non-negative")
    return np.random.default_rng(np.random.SeedSequence([int(seed), int(stream)]))


def _softmax(logits: np.ndarray) -> np.ndarray:
    """Numerically stable softmax evaluated in float64."""
    shifted = np.asarray(logits, dtype=np.float64)
    shifted = shifted - shifted.max(axis=-1, keepdims=True)
    values = np.exp(shifted)
    return values / values.sum(axis=-1, keepdims=True)


def generate_mechanism_weights(
    d_tilde: int = 8,
    n_classes: int = 5,
    seed: int = 42,
) -> np.ndarray:
    """Generate the fixed mechanism independently of the sample count ``n``."""
    if d_tilde <= 0 or n_classes <= 1:
        raise ValueError("d_tilde must be positive and n_classes must exceed one")
    rng = _make_rng(seed, _MECHANISM_STREAM)
    return (rng.standard_normal((d_tilde, n_classes)) * 0.5).astype(np.float32)


def generate_contexts(n: int = 1000, d_tilde: int = 8, seed: int = 42) -> np.ndarray:
    """Generate only public contexts, used by the ground-truth-only fast path."""
    if n <= 0 or d_tilde <= 0:
        raise ValueError("n and d_tilde must be positive")
    rng = _make_rng(seed, _DATA_STREAM)
    return rng.standard_normal((n, d_tilde)).astype(np.float32)


def _draw_ground_truth_noise(
    n_samples: int,
    n_classes: int,
    noise_std: float,
    seed: int,
) -> np.ndarray:
    """Draw a reusable antithetic Monte Carlo grid for logit-noise integration."""
    rng = _make_rng(seed, _GROUND_TRUTH_STREAM)
    half = n_samples // 2
    positive = rng.standard_normal((half, n_classes))
    pieces = [positive, -positive]
    if n_samples % 2:
        pieces.append(rng.standard_normal((1, n_classes)))
    return np.concatenate(pieces, axis=0)[:n_samples] * noise_std


def _mean_softmax_with_noise(
    base_logits: np.ndarray,
    noise_samples: np.ndarray,
) -> np.ndarray:
    """Average softmax(base_logits + noise) without retaining all task batches."""
    work = base_logits[:, None, :] + noise_samples[None, :, :]
    work -= work.max(axis=-1, keepdims=True)
    np.exp(work, out=work)
    work /= work.sum(axis=-1, keepdims=True)
    return work.mean(axis=1)


def conditional_action_probabilities(
    T: np.ndarray,
    W: np.ndarray,
    beta_h: float,
    *,
    noise_std: float = DEFAULT_NOISE_STD,
    gt_inner_samples: int = DEFAULT_GT_INNER_SAMPLES,
    gt_seed: int = DEFAULT_GT_SEED,
    gt_batch_size: int = DEFAULT_GT_BATCH_SIZE,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute ``q_h(a|T) = E_noise softmax(TW + beta*h*e_0 + noise)``.

    The inner expectation uses a fixed antithetic Monte Carlo grid and processes
    contexts in batches.  Peak working memory is therefore proportional to
    ``gt_batch_size * gt_inner_samples * n_classes``, rather than to the full
    number of contexts.
    """
    T64 = np.asarray(T, dtype=np.float64)
    W64 = np.asarray(W, dtype=np.float64)
    if T64.ndim != 2 or W64.ndim != 2 or T64.shape[1] != W64.shape[0]:
        raise ValueError("T and W must be compatible two-dimensional arrays")
    if len(T64) == 0:
        raise ValueError("T must contain at least one context")
    if not np.isfinite(beta_h):
        raise ValueError("beta_h must be finite")
    if not np.isfinite(noise_std) or noise_std < 0:
        raise ValueError("noise_std must be finite and non-negative")
    if gt_inner_samples <= 0 or gt_batch_size <= 0:
        raise ValueError("gt_inner_samples and gt_batch_size must be positive")

    # ``einsum`` avoids spurious floating-point status warnings emitted by some
    # macOS Accelerate-backed ``matmul`` builds for otherwise finite operands.
    base = np.einsum("nd,dk->nk", T64, W64, optimize=True)
    if not np.isfinite(base).all():
        raise FloatingPointError("non-finite base logits in ground-truth calculation")
    shifted = base.copy()
    shifted[:, 0] += beta_h
    if noise_std == 0.0:
        return _softmax(base), _softmax(shifted)

    noise = _draw_ground_truth_noise(
        gt_inner_samples,
        W64.shape[1],
        noise_std,
        gt_seed,
    )
    q0 = np.empty_like(base)
    q1 = np.empty_like(base)
    for start in range(0, len(base), gt_batch_size):
        stop = min(start + gt_batch_size, len(base))
        q0[start:stop] = _mean_softmax_with_noise(base[start:stop], noise)
        q1[start:stop] = _mean_softmax_with_noise(shifted[start:stop], noise)
    return q0, q1


def true_conditional_mi(
    T: np.ndarray,
    W: np.ndarray,
    beta_h: float,
    *,
    noise_std: float = DEFAULT_NOISE_STD,
    gt_inner_samples: int = DEFAULT_GT_INNER_SAMPLES,
    gt_seed: int = DEFAULT_GT_SEED,
    gt_batch_size: int = DEFAULT_GT_BATCH_SIZE,
) -> float:
    """Return ``I(H; A | T)`` in nats for a balanced Bernoulli hidden state.

    This integrates out logit noise and sums over the full action distribution.
    It intentionally accepts neither sampled hidden states nor sampled actions.
    For nonzero ``noise_std`` the inner noise expectation is a reproducible
    Monte Carlo approximation whose resolution is ``gt_inner_samples``.
    """
    if not np.isfinite(noise_std) or noise_std < 0:
        raise ValueError("noise_std must be finite and non-negative")
    if gt_inner_samples <= 0 or gt_batch_size <= 0:
        raise ValueError("gt_inner_samples and gt_batch_size must be positive")
    if beta_h == 0.0:
        # The two conditional laws are identical for every T and every noise law.
        return 0.0

    q0, q1 = conditional_action_probabilities(
        T,
        W,
        beta_h,
        noise_std=noise_std,
        gt_inner_samples=gt_inner_samples,
        gt_seed=gt_seed,
        gt_batch_size=gt_batch_size,
    )
    marginal = 0.5 * (q0 + q1)

    def row_kl(p: np.ndarray, q: np.ndarray) -> np.ndarray:
        terms = np.zeros_like(p)
        mask = p > 0.0
        terms[mask] = p[mask] * (np.log(p[mask]) - np.log(q[mask]))
        return terms.sum(axis=1)

    per_context = 0.5 * row_kl(q0, marginal) + 0.5 * row_kl(q1, marginal)
    return max(0.0, float(per_context.mean()))


def generate_data(
    n=1000,
    d_tilde=8,
    n_classes=5,
    beta_h=0.0,
    seed=42,
    *,
    mechanism_seed=42,
    action_seed: int | None = None,
    noise_std: float = DEFAULT_NOISE_STD,
    gt_inner_samples: int = DEFAULT_GT_INNER_SAMPLES,
    gt_seed: int = DEFAULT_GT_SEED,
    gt_batch_size: int = DEFAULT_GT_BATCH_SIZE,
    W: np.ndarray | None = None,
):
    """Generate synthetic data with controlled hidden influence.

    P(A = k | T, H, epsilon)
      = softmax(T @ W_k + beta_h * H * delta_{k,0} + epsilon_k),
    where epsilon_k ~ Normal(0, noise_std^2).

    beta_h=0 -> H has no influence -> I(H;A|T)=0
    Larger beta_h -> stronger influence -> higher conditional MI.
    """
    if n <= 0 or d_tilde <= 0 or n_classes <= 1:
        raise ValueError("n and d_tilde must be positive and n_classes must exceed one")
    if not np.isfinite(noise_std) or noise_std < 0:
        raise ValueError("noise_std must be finite and non-negative")

    data_rng = _make_rng(seed, _DATA_STREAM)
    sample_action_rng = _make_rng(
        seed if action_seed is None else action_seed,
        _ACTION_STREAM,
    )
    T = data_rng.standard_normal((n, d_tilde)).astype(np.float32)
    H = (data_rng.random(n) > 0.5).astype(np.float32)
    if W is None:
        W = generate_mechanism_weights(d_tilde, n_classes, mechanism_seed)
    else:
        W = np.asarray(W, dtype=np.float32)
        if W.shape != (d_tilde, n_classes):
            raise ValueError(
                f"W must have shape {(d_tilde, n_classes)}, got {W.shape}"
            )

    logits = np.einsum(
        "nd,dk->nk",
        T.astype(np.float64),
        W.astype(np.float64),
        optimize=True,
    )
    # H pushes toward class 0
    bias = np.zeros((n, n_classes), dtype=np.float32)
    bias[:, 0] = beta_h * H
    sample_noise = data_rng.standard_normal((n, n_classes)) * noise_std
    probs = _softmax(logits + bias + sample_noise)
    A = np.array(
        [sample_action_rng.choice(n_classes, p=p) for p in probs],
        dtype=np.int64,
    )

    true_mi = true_conditional_mi(
        T,
        W,
        beta_h,
        noise_std=noise_std,
        gt_inner_samples=gt_inner_samples,
        gt_seed=gt_seed,
        gt_batch_size=gt_batch_size,
    )

    return T, H, A, probs, true_mi


def ce_diff_estimate(T, H, A, n_classes, n_folds=5):
    """Cross-validated CE-diff: I_hat = L(T) - L(T,H)."""
    import torch
    import torch.nn as nn
    import torch.optim as optim

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
    try:
        from .synthetic_v3_estimator import run_v3_estimation
    except ImportError:
        import sys

        module_dir = str(Path(__file__).resolve().parent)
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        from synthetic_v3_estimator import run_v3_estimation

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
         estimator: str = "legacy",
         noise_std: float = DEFAULT_NOISE_STD,
         gt_inner_samples: int = DEFAULT_GT_INNER_SAMPLES,
         gt_seed: int = DEFAULT_GT_SEED,
         gt_batch_size: int = DEFAULT_GT_BATCH_SIZE,
         ground_truth_only: bool = False,
         seed: int = 42,
         mechanism_seed: int = 42):
    if beta_levels is None:
        beta_levels = [0.0, 0.5, 1.0, 2.0, 4.0]
    if n_trajectories <= 0:
        raise ValueError("n_trajectories must be positive")
    if not np.isfinite(noise_std) or noise_std < 0:
        raise ValueError("noise_std must be finite and non-negative")
    if gt_inner_samples <= 0 or gt_batch_size <= 0:
        raise ValueError("gt_inner_samples and gt_batch_size must be positive")

    results = []
    d_tilde = 8
    n_classes = 5
    W = generate_mechanism_weights(d_tilde, n_classes, mechanism_seed)
    ground_truth_contexts = (
        generate_contexts(n_trajectories, d_tilde, seed)
        if ground_truth_only
        else None
    )

    mode = "ground-truth-only" if ground_truth_only else f"{estimator} estimator"
    print(
        f"Running {mode} (noise_std={noise_std}, "
        f"gt_inner_samples={gt_inner_samples}, gt_seed={gt_seed})..."
    )

    for beta_h in beta_levels:
        if ground_truth_only:
            assert ground_truth_contexts is not None
            true_mi = true_conditional_mi(
                ground_truth_contexts,
                W,
                beta_h,
                noise_std=noise_std,
                gt_inner_samples=gt_inner_samples,
                gt_seed=gt_seed,
                gt_batch_size=gt_batch_size,
            )
            T = H = A = probs = None
        else:
            T, H, A, probs, true_mi = generate_data(
                n=n_trajectories,
                d_tilde=d_tilde,
                n_classes=n_classes,
                beta_h=beta_h,
                seed=seed,
                mechanism_seed=mechanism_seed,
                noise_std=noise_std,
                gt_inner_samples=gt_inner_samples,
                gt_seed=gt_seed,
                gt_batch_size=gt_batch_size,
                W=W,
            )
        true_mi_bits = true_mi / np.log(2)
        ground_truth_metadata = {
            "n": int(n_trajectories),
            "d_tilde": d_tilde,
            "n_classes": n_classes,
            "noise_std": float(noise_std),
            "data_seed": int(seed),
            "mechanism_seed": int(mechanism_seed),
            "gt_method": (
                "exact_softmax_sum" if noise_std == 0.0
                else "antithetic_inner_monte_carlo"
            ),
            "gt_inner_samples": int(gt_inner_samples),
            "gt_seed": int(gt_seed),
            "gt_batch_size": int(gt_batch_size),
        }

        if ground_truth_only:
            results.append({
                "beta_h": float(beta_h),
                "true_mi_nats": float(true_mi),
                "true_mi_bits": float(true_mi_bits),
                **ground_truth_metadata,
            })
            print(f"  beta={beta_h:.1f}: true_MI={true_mi_bits:.6f} bits")
            continue

        if estimator == "legacy":
            assert T is not None and H is not None and A is not None
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
                **ground_truth_metadata,
            })
            bound_ok = "OK" if delta_bits <= true_mi_bits else "VIOLATION"
            print(f"  beta={beta_h:.1f}: true_MI={true_mi_bits:.4f} bits, "
                  f"delta^LB={delta_bits:.4f} bits, eps^UB=1.0 bits [{bound_ok}]")

        elif estimator == "v3":
            assert T is not None and H is not None and A is not None
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
                "n_null_repeats": int(v3_result["n_null_repeats"]),
                "task_grouping": str(v3_result["task_grouping"]),
                **ground_truth_metadata,
            })

            status = "OK" if null_pass else "INVALID"
            cert_str = f"{certified_delta_LB_bits:.4f}" if certified_delta_LB_bits is not None else "None"
            print(f"  beta={beta_h:.1f}: true_MI={true_mi_bits:.4f} bits, "
                  f"raw_gap={raw_gap_bits:.4f} bits, null_p95={null_p95_bits:.4f} bits, "
                  f"cert_delta_LB={cert_str} bits [{status}]")

        else:
            raise ValueError(f"Unknown estimator: {estimator}")

    # Ground-truth-only runs use a separate file and never overwrite old results.
    if ground_truth_only:
        out_file = "synthetic_ground_truth.json"
    elif estimator == "legacy":
        out_file = "synthetic_results.json"
    else:
        out_file = "synthetic_results_v3.json"

    out = Path(out_dir) / out_file
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out}")

    # Generate figure (only for legacy for now)
    if not ground_truth_only and not skip_plot and estimator == "legacy":
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
    parser.add_argument("--noise-std", type=float, default=DEFAULT_NOISE_STD,
                        help="Std. dev. of independent Gaussian logit noise (default: 0.1)")
    parser.add_argument("--gt-inner-samples", type=int, default=DEFAULT_GT_INNER_SAMPLES,
                        help="Inner noise samples used for true MI integration")
    parser.add_argument("--gt-seed", type=int, default=DEFAULT_GT_SEED,
                        help="Independent seed for true MI noise integration")
    parser.add_argument("--gt-batch-size", type=int, default=DEFAULT_GT_BATCH_SIZE,
                        help="Context batch size controlling GT integration memory")
    parser.add_argument("--ground-truth-only", action="store_true",
                        help="Compute true MI only; skip neural estimators and use a separate output file")
    parser.add_argument("--seed", type=int, default=42,
                        help="Data-generating seed (default: 42)")
    parser.add_argument("--mechanism-seed", type=int, default=42,
                        help="Fixed mechanism-W seed, independent of sample count")
    args = parser.parse_args()
    main(n_trajectories=args.n_trajectories, beta_levels=args.beta_levels,
         out_dir=args.out_dir, skip_plot=args.no_plot, estimator=args.estimator,
         noise_std=args.noise_std, gt_inner_samples=args.gt_inner_samples,
         gt_seed=args.gt_seed, gt_batch_size=args.gt_batch_size,
         ground_truth_only=args.ground_truth_only, seed=args.seed,
         mechanism_seed=args.mechanism_seed)
