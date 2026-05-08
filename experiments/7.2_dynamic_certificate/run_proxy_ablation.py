"""Proxy resolution ablation for §7.2.

Runs CE-diff estimator across proxy resolution levels:
  random, permuted, d1, d3, d5, d16, d64, d128
with choice of regularized predictor (logistic_l2 or mlp).

Predictors use predict_proba (required for cross-entropy computation).
RidgeClassifier does NOT provide predict_proba — deliberately excluded.

Usage:
  python run_proxy_ablation.py --pairs pairs.pt --predictor logistic_l2 --out data/processed/proxy_ablation.json
  python run_proxy_ablation.py --pairs pairs.pt --predictor mlp --d-z 3584 --out data/processed/proxy_ablation.json
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import torch

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegressionCV
from sklearn.neural_network import MLPClassifier


def _get_folds(A: np.ndarray, n_splits: int = 5) -> list[np.ndarray]:
    """Stratified fold assignment."""
    N = len(A)
    classes = np.unique(A)
    indices = np.arange(N)
    folds = [[] for _ in range(n_splits)]
    for c in classes:
        c_indices = indices[A == c]
        rng = np.random.RandomState(42)
        rng.shuffle(c_indices)
        for i, idx in enumerate(c_indices):
            folds[i % n_splits].append(idx)
    for f in folds:
        rng = np.random.RandomState(42)
        rng.shuffle(f)
    return [np.array(f) for f in folds]


def _make_predictor(predictor_type: str, num_classes: int):
    """Create sklearn predictor with predict_proba support."""
    if predictor_type == "logistic_l2":
        return LogisticRegressionCV(
            Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
            max_iter=2000,
            random_state=42,
            n_jobs=-1,
        )
    elif predictor_type == "mlp":
        return MLPClassifier(
            hidden_layer_sizes=(128,),
            activation='relu',
            alpha=0.01,
            batch_size=64,
            learning_rate_init=0.001,
            max_iter=200,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=10,
            random_state=42,
        )
    else:
        raise ValueError(f"Unknown predictor: {predictor_type}. Use 'logistic_l2' or 'mlp'.")


def _ce_diff_estimate(Phi: np.ndarray, Z: np.ndarray, A: np.ndarray,
                      predictor_type: str = "logistic_l2") -> dict:
    """Cross-fitted CE-diff: I(Z;A|Phi) ~= L(Phi) - L(Phi,Z).

    Uses 5-fold cross-fitting with sklearn predict_proba.
    Hold-out log-loss is computed from predicted probabilities.
    """
    N = len(A)
    num_classes = int(A.max()) + 1
    folds = _get_folds(A, n_splits=5)
    oof_l_trace = np.zeros(N)
    oof_l_proxy = np.zeros(N)

    for i in range(5):
        test_idx = folds[i]
        train_idx = np.concatenate([folds[j] for j in range(5) if j != i])

        Phi_train, Phi_test = Phi[train_idx], Phi[test_idx]
        Z_train, Z_test = Z[train_idx], Z[test_idx]
        A_train, A_test = A[train_idx], A[test_idx]

        # Trace-only model
        m_trace = _make_predictor(predictor_type, num_classes)
        m_trace.fit(Phi_train, A_train)
        probs_trace = m_trace.predict_proba(Phi_test)

        # Proxy model (trace + Z)
        X_train_p = np.concatenate([Phi_train, Z_train], axis=1)
        X_test_p = np.concatenate([Phi_test, Z_test], axis=1)
        m_proxy = _make_predictor(predictor_type, num_classes)
        m_proxy.fit(X_train_p, A_train)
        probs_proxy = m_proxy.predict_proba(X_test_p)

        for k, idx in enumerate(test_idx):
            val = A[idx]
            oof_l_trace[idx] = -np.log(max(probs_trace[k, val], 1e-10))
            oof_l_proxy[idx] = -np.log(max(probs_proxy[k, val], 1e-10))

    l_trace = float(np.mean(oof_l_trace))
    l_proxy = float(np.mean(oof_l_proxy))
    delta = l_trace - l_proxy

    sample_mi = oof_l_trace - oof_l_proxy
    bootstraps = []
    rng = np.random.RandomState(42)
    for _ in range(1000):
        idx = rng.choice(N, N, replace=True)
        bootstraps.append(float(np.mean(sample_mi[idx])))
    ci_lo, ci_hi = np.percentile(bootstraps, [2.5, 97.5])

    return {
        "estimator": "ce_diff_oof",
        "predictor": predictor_type,
        "L_trace": l_trace,
        "L_trace_proxy": l_proxy,
        "delta_act_lb_nats": delta,
        "delta_act_lb_bits": delta / np.log(2),
        "ci_95_nats": [float(ci_lo), float(ci_hi)],
        "ci_95_bits": [float(ci_lo) / np.log(2), float(ci_hi) / np.log(2)],
        "n": int(N),
    }


def make_random_proxy(Z_shape: tuple) -> np.ndarray:
    rng = np.random.RandomState(42)
    return rng.randn(*Z_shape).astype(np.float32)


def make_permuted_proxy(Z: np.ndarray, A: np.ndarray) -> np.ndarray:
    Zp = Z.copy()
    rng = np.random.RandomState(42)
    for c in np.unique(A):
        mask = A == c
        Zp[mask] = rng.permutation(Zp[mask])
    return Zp


def make_pca_proxy(Z: np.ndarray, d: int) -> np.ndarray:
    if Z.shape[1] <= d:
        return Z
    pca = PCA(n_components=d, random_state=42)
    return pca.fit_transform(Z).astype(np.float32)


def run_proxy_ablation(pairs_path: str, out_path: str,
                       predictor_type: str = "logistic_l2",
                       d_z: int | None = None,
                       meta_path: str | None = None) -> dict:
    """Run proxy ablation: controls + PCA resolution sweep."""
    data = torch.load(pairs_path, map_location="cpu")

    # Determine d_z: explicit > meta > default
    if d_z is None and meta_path:
        with open(meta_path) as f:
            meta = json.load(f)
        d_z = meta.get("d_z", 10)

    if d_z is None:
        d_z = 10

    # Sanity: if d_z > half the columns, cap at 1/3
    if d_z >= data.shape[1] // 2:
        d_z = min(d_z, data.shape[1] // 3)

    Z_full = data[:, :d_z].numpy()
    Phi = data[:, d_z:-1].numpy()
    A = data[:, -1].numpy().astype(int)

    N = len(A)
    if N < 20:
        return {"error": f"too few samples: {N}", "n": N}

    print(f"N={N}, d_z={d_z}, d_phi={Phi.shape[1]}, "
          f"num_classes={int(A.max())+1}, predictor={predictor_type}")

    results = {}

    # Controls
    print("  random control...")
    Z_rand = make_random_proxy(Z_full.shape)
    results["random"] = _ce_diff_estimate(Phi, Z_rand, A, predictor_type)

    print("  permuted control...")
    Z_perm = make_permuted_proxy(Z_full, A)
    results["permuted"] = _ce_diff_estimate(Phi, Z_perm, A, predictor_type)

    # PCA resolution sweep
    pca_dims = [1, 3, 5, 16, 64, 128]
    for d in pca_dims:
        if d > Z_full.shape[1]:
            continue
        print(f"  PCA d={d}...")
        Z_pca = make_pca_proxy(Z_full, d)
        results[f"d{d}"] = _ce_diff_estimate(Phi, Z_pca, A, predictor_type)

    # Full proxy (no PCA)
    print("  full proxy (no PCA)...")
    results["full"] = _ce_diff_estimate(Phi, Z_full, A, predictor_type)

    summary = {
        "n": N,
        "n_classes": int(A.max()) + 1,
        "predictor": predictor_type,
        "d_z_raw": d_z,
        "d_phi": Phi.shape[1],
        "proxy_dims": {k: v.get("delta_act_lb_nats") for k, v in results.items()},
        "details": results,
    }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=float)

    # Print summary
    print(f"\n{'Proxy':12s}  {'delta_LB (nats)':>14s}  {'delta_LB (bits)':>14s}  {'95% CI (bits)'}")
    print("-" * 60)
    for level, r in results.items():
        bits = r.get("delta_act_lb_bits", 0.0)
        ci = r.get("ci_95_bits", [0, 0])
        print(f"  {level:10s}  {r['delta_act_lb_nats']:14.4f}  {bits:14.4f}  "
              f"[{ci[0]:.4f}, {ci[1]:.4f}]")

    # Best non-negative result
    valid = [(k, v) for k, v in results.items()
             if k not in ("random", "permuted") and v.get("delta_act_lb_nats", -1) > 0]
    if valid:
        best_k, best_v = max(valid, key=lambda x: x[1]["delta_act_lb_nats"])
        print(f"\nBest: {best_k} -> {best_v['delta_act_lb_nats']:.4f} nats "
              f"= {best_v['delta_act_lb_bits']:.4f} bits")

    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True)
    parser.add_argument("--meta", default=None)
    parser.add_argument("--d-z", type=int, default=None,
                        help="Override proxy dimension (default: from meta or 10)")
    parser.add_argument("--predictor", default="logistic_l2",
                        choices=["logistic_l2", "mlp"],
                        help="Predictor class (default: logistic_l2)")
    parser.add_argument("--out", default="data/processed/proxy_ablation.json")
    args = parser.parse_args()
    run_proxy_ablation(args.pairs, args.out, args.predictor,
                       args.d_z, args.meta)
