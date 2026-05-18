"""synthetic_v3_estimator.py

This module contains the v3 estimator logic adapted from
`experiments/7.2_dynamic_certificate/diagnose_v3.py`.
The original source file's git commit is `fa6696d7f16729bbd8209f7829e6d31edd57dd42`.
"""
from __future__ import annotations

import sys, warnings
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Constants from diagnose_v3.py
PHI_PCA_DIM = 128
N_OUTER_FOLDS = 5
N_NULL_REPEATS = 20
SEED_LABEL = 42
SEED_ZPERM = 99
CS_GRID = [0.001, 0.01, 0.1, 1.0, 10.0]


def _make_outer_folds(A, task_ids, rng_seed):
    """StratifiedGroupKFold outer splits. Falls back to KFold if too few groups."""
    unique_classes = np.unique(A)
    label_map = {orig: i for i, orig in enumerate(unique_classes)}
    A_remapped = np.array([label_map[a] for a in A])
    n_groups = len(np.unique(task_ids))
    n_splits = min(N_OUTER_FOLDS, n_groups)
    if n_splits < 2:
        n_splits = 2
    try:
        sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True,
                                     random_state=rng_seed)
        folds = list(sgkf.split(np.zeros(len(A)), A_remapped, groups=task_ids))
    except ValueError:
        from sklearn.model_selection import KFold
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=rng_seed)
        folds = list(kf.split(np.zeros(len(A))))
    return folds, A_remapped, n_splits


def _eval_one(Z_raw, Phi_raw, A_in, task_ids, dim_z, folds, rng_seed):
    """Manual per-fold pipeline. Returns dict with CE, gap, diagnostics."""
    N = len(A_in)
    n_classes = len(np.unique(A_in))
    oof_l_trace = np.full(N, np.nan)
    oof_l_proxy = np.full(N, np.nan)
    chosen_Cs = []

    for fold_i, (train_idx, test_idx) in enumerate(folds):
        Phi_train_raw = Phi_raw[train_idx]
        Phi_test_raw  = Phi_raw[test_idx]
        Z_train_raw   = Z_raw[train_idx]
        Z_test_raw    = Z_raw[test_idx]
        A_train       = A_in[train_idx]
        A_test        = A_in[test_idx]
        T_train       = task_ids[train_idx]
        # T_test        = task_ids[test_idx] # Not used

        n_train_groups = len(np.unique(T_train))
        inner_n_splits = max(2, min(4, n_train_groups,
                                    min(np.bincount(A_train))) if len(np.unique(A_train)) > 1 else 2)
        inner_cv = GroupKFold(n_splits=inner_n_splits)

        # --- scale Phi ---
        phi_scaler = StandardScaler()
        Phi_train_s = phi_scaler.fit_transform(Phi_train_raw).astype(np.float32)
        Phi_test_s  = phi_scaler.transform(Phi_test_raw).astype(np.float32)

        # --- PCA Phi ---
        actual_phi_dim = min(PHI_PCA_DIM, len(train_idx), Phi_train_s.shape[1])
        phi_pca = PCA(n_components=actual_phi_dim, svd_solver="full")
        Phi_train_p = phi_pca.fit_transform(Phi_train_s).astype(np.float32)
        Phi_test_p  = phi_pca.transform(Phi_test_s).astype(np.float32)

        # --- scale + PCA Z (manual, fit on train only) ---
        z_scaler = StandardScaler()
        Z_train_s = z_scaler.fit_transform(Z_train_raw).astype(np.float32)
        Z_test_s  = z_scaler.transform(Z_test_raw).astype(np.float32)

        actual_z_dim = min(dim_z, len(train_idx), Z_train_s.shape[1])
        z_pca = PCA(n_components=actual_z_dim, svd_solver="full")
        Z_train_p = z_pca.fit_transform(Z_train_s).astype(np.float32)
        Z_test_p  = z_pca.transform(Z_test_s).astype(np.float32)

        # --- trace model (Phi only) ---
        grid_trace = GridSearchCV(
            estimator=LogisticRegression(max_iter=5000),
            param_grid={"C": CS_GRID},
            cv=inner_cv,
            scoring="neg_log_loss"
        )
        grid_trace.fit(Phi_train_p, A_train, groups=T_train)
        probs_trace = grid_trace.predict_proba(Phi_test_p)
        trace_classes = {c: i for i, c in enumerate(grid_trace.best_estimator_.classes_)}

        # --- proxy model (Phi_pca + Z_pca) ---
        X_train_p = np.concatenate([Phi_train_p, Z_train_p], axis=1)
        X_test_p  = np.concatenate([Phi_test_p, Z_test_p], axis=1)
        grid_proxy = GridSearchCV(
            estimator=LogisticRegression(max_iter=5000),
            param_grid={"C": CS_GRID},
            cv=inner_cv,
            scoring="neg_log_loss"
        )
        grid_proxy.fit(X_train_p, A_train, groups=T_train)
        probs_proxy = grid_proxy.predict_proba(X_test_p)
        proxy_classes = {c: i for i, c in enumerate(grid_proxy.best_estimator_.classes_)}

        chosen_Cs.append(float(grid_proxy.best_params_["C"]))

        # --- OOF log-loss ---
        for k, idx in enumerate(test_idx):
            val = A_in[idx]
            p_trace = probs_trace[k, trace_classes[val]] if val in trace_classes else 1e-10
            p_proxy = probs_proxy[k, proxy_classes[val]] if val in proxy_classes else 1e-10
            oof_l_trace[idx] = -np.log(max(p_trace, 1e-10))
            oof_l_proxy[idx] = -np.log(max(p_proxy, 1e-10))

    ce_trace = float(np.mean(oof_l_trace[~np.isnan(oof_l_trace)]))
    ce_proxy = float(np.mean(oof_l_proxy[~np.isnan(oof_l_proxy)]))
    gap_bits = (ce_trace - ce_proxy) / np.log(2)

    return {
        "ce_trace": ce_trace,
        "ce_proxy": ce_proxy,
        "gap_bits": gap_bits,
    }


def run_v3_estimation(Phi_raw, Z_raw, A_in, task_ids, rng_seed=42):
    """Run real-Z (dim=1), gaussian-Z (dim=1), and permuted-Z (dim=1)."""
    N = len(A_in)

    # Build StratifiedGroupKFold
    folds, A_remapped, n_splits = _make_outer_folds(A_in, task_ids, rng_seed)

    # --- Real Z at dim=1 ---
    dim_z = 1 # As per plan, use dim_z=1 only
    res_real = _eval_one(Z_raw, Phi_raw, A_remapped, task_ids, dim_z, folds, rng_seed)
    raw_gap_bits = res_real["gap_bits"]

    # --- Repeated null suite ---
    null_gaps_gaussian = []
    null_gaps_permuted = []

    for b in range(N_NULL_REPEATS):
        rng_label = np.random.RandomState(SEED_LABEL + b)
        A_shuf = A_remapped.copy()
        rng_label.shuffle(A_shuf)

        # Gaussian-Z null
        Z_gauss_null = np.random.RandomState(rng_seed + b).randn(
            N, Z_raw.shape[1]).astype(np.float32)
        res_gn = _eval_one(Z_gauss_null, Phi_raw, A_shuf, task_ids, dim_z, folds, rng_seed)
        null_gaps_gaussian.append(res_gn["gap_bits"])

        # Permuted-Z null (global permutation with fresh seed per repeat)
        rng_pn = np.random.default_rng(SEED_ZPERM + b * 100)
        Z_perm_null = rng_pn.permutation(Z_raw, axis=0).astype(np.float32)
        res_pn = _eval_one(Z_perm_null, Phi_raw, A_shuf, task_ids, dim_z, folds, rng_seed)
        null_gaps_permuted.append(res_pn["gap_bits"])

    # Null p95
    null_p95 = max(np.percentile(null_gaps_gaussian, 95),
                   np.percentile(null_gaps_permuted, 95))

    # Null gating: if any single null repeat shows |gap| > 0.5, pipeline invalid
    max_null_gap = max(max(abs(g) for g in null_gaps_gaussian),
                       max(abs(g) for g in null_gaps_permuted))
    null_pass = max_null_gap < 0.5

    # Conservative certificate
    null_corrected_gap_bits = raw_gap_bits - null_p95
    certified_delta_LB_bits = max(0.0, null_corrected_gap_bits) if null_pass else None # If null_pass is false, pipeline invalid

    return {
        "raw_gap_bits": raw_gap_bits,
        "null_p95_bits": null_p95,
        "null_corrected_gap_bits": null_corrected_gap_bits,
        "certified_delta_LB_bits": certified_delta_LB_bits,
        "null_pass": null_pass,
        "n_null_repeats": N_NULL_REPEATS,
        "task_grouping": "singleton"
    }
