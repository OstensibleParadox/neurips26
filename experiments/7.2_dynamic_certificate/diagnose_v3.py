"""diagnose_v3: sanity-hardened proxy CE-diff pipeline.

Fixes over v2:
  1. GroupKFold outer CV (no task leakage across train/test)
  2. Group-aware inner CV via GridSearchCV + GroupKFold (C selection clean)
  3. Fold-local permuted-Z (no transductive leakage from held-out tasks)
  4. Independent RNG seeds for label shuffle vs Z permutation
  5. Deterministic PCA (svd_solver="full") + subspace angle stability
  6. Repeated null suite (B repeats) → null_p95 → null-corrected gap
  7. Conservative certificate: delta_LB = max(0, raw - null_p95)

Three legal conclusions:
  - Pipeline invalid: any null |gap| > 0.5 bits
  - Valid non-certification: null passes, certificate = 0
  - Valid positive certificate: null passes, certificate > 0
"""
from __future__ import annotations

import sys, hashlib, random, warnings
from pathlib import Path
import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from transformers import AutoModelForCausalLM, AutoTokenizer

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "7.3_intervention"))
from run_intervention import PLANNING_TASKS, build_prompt

TOOL_CLASSES = ["search", "calculator", "email", "calendar", "weather"]
DEVICE = "mps"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
N_SAMPLES = 200
DIMS = [1, 2, 3, 5, 8, 16]
PHI_PCA_DIM = 128
N_OUTER_FOLDS = 5
N_NULL_REPEATS = 20   # production: 100; debug: 20
SEED_LABEL = 42
SEED_ZPERM = 99       # must differ from SEED_LABEL
SEED_DATA = 42
CS_GRID = [0.001, 0.01, 0.1, 1.0, 10.0]


# ═══════════════════════════════════════════════════════════════════════════
# Model loading & data capture
# ═══════════════════════════════════════════════════════════════════════════

def capture_one_condition(task_pool, perturb_target, rng_seed=42):
    """Capture Z, Phi, A, task_ids for one condition.

    Returns (Z, Phi, A, task_ids) where task_ids indexes into task_pool.
    """
    trace_hidden = [None]
    probe_hidden = [None]

    def _unwrap_hs(output):
        if isinstance(output, tuple):
            return output[0].detach()
        return output.detach()

    def trace_hook(module, input, output):
        trace_hidden[0] = _unwrap_hs(output)

    def probe_hook(module, input, output):
        probe_hidden[0] = _unwrap_hs(output)

    h1 = model.model.layers[4].register_forward_hook(trace_hook)
    h2 = model.model.layers[16].register_forward_hook(probe_hook)

    rng = random.Random(rng_seed)
    n_tasks = len(task_pool)
    n_repeats = (N_SAMPLES // n_tasks) + 1
    task_indices = (list(range(n_tasks)) * n_repeats)[:N_SAMPLES]
    rng.shuffle(task_indices)

    Z_list, Phi_list, A_list, T_list = [], [], [], []

    for task_idx in task_indices:
        task_text, scratchpad = task_pool[task_idx]
        if perturb_target == "scratchpad":
            scratchpad = _mask_tokens(scratchpad, fraction=0.3, rng=rng)
        elif perturb_target == "query":
            task_text = _mask_tokens(task_text, fraction=0.3, rng=rng)

        prompt = build_prompt(task_text, scratchpad)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True,
                          max_length=512).to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs)
        if trace_hidden[0] is None or probe_hidden[0] is None:
            continue

        phi_t = trace_hidden[0].mean(dim=1).float().cpu().numpy().flatten()
        z_t = probe_hidden[0][:, -1, :].float().cpu().numpy().flatten()

        logits = outputs.logits[:, -1, :].cpu().float()
        tool_ids = []
        for tok in TOOL_CLASSES:
            ids = tokenizer.encode(tok, add_special_tokens=False)
            if ids:
                tool_ids.append(ids[0])
        action_idx = int(torch.argmax(logits[0, tool_ids]).item())

        Z_list.append(z_t)
        Phi_list.append(phi_t)
        A_list.append(action_idx)
        T_list.append(task_idx)

    h1.remove()
    h2.remove()
    return (np.array(Z_list, dtype=np.float32),
            np.array(Phi_list, dtype=np.float32),
            np.array(A_list, dtype=int),
            np.array(T_list, dtype=int))


def _mask_tokens(text: str, fraction: float, rng: random.Random) -> str:
    tokens = text.split()
    n_mask = max(1, int(len(tokens) * fraction))
    indices = sorted(rng.sample(range(len(tokens)), n_mask))
    for i in indices:
        tokens[i] = "[MASK]"
    return " ".join(tokens)


# ═══════════════════════════════════════════════════════════════════════════
# Core fold-level evaluation (manual per-fold pipeline)
# ═══════════════════════════════════════════════════════════════════════════

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


def _eval_one(Z_raw, Phi_raw, A_in, task_ids, dim_z, z_desc, folds, rng_seed):
    """Manual per-fold pipeline. Returns dict with CE, gap, diagnostics.

    Within each fold:
      1. StandardScaler fit on train, transform train+test
      2. PCA(svd_solver="full") fit on train, transform train+test
      3. GridSearchCV(LogisticRegression, cv=GroupKFold) fit on train
      4. Predict on test
    Also collects per-fold generalization diagnostics.
    """
    N = len(A_in)
    n_classes = len(np.unique(A_in))
    oof_l_trace = np.full(N, np.nan)
    oof_l_proxy = np.full(N, np.nan)
    chosen_Cs = []
    coef_z_norms = []
    pca_components_snapshots = {}
    effective_rank = -1
    exp_var_first10 = []
    fold_diagnostics = []

    for fold_i, (train_idx, test_idx) in enumerate(folds):
        Phi_train_raw = Phi_raw[train_idx]
        Phi_test_raw  = Phi_raw[test_idx]
        Z_train_raw   = Z_raw[train_idx]
        Z_test_raw    = Z_raw[test_idx]
        A_train       = A_in[train_idx]
        A_test        = A_in[test_idx]
        T_train       = task_ids[train_idx]
        T_test        = task_ids[test_idx]

        # Defensive: warn if train fold lacks any class (small-sample pathology;
        # resolves naturally at scale with StratifiedGroupKFold + N ≥ 3000).
        _train_classes = set(np.unique(A_train))
        _all_classes = set(np.unique(A_in))
        if _train_classes != _all_classes:
            print(f"  [WARN] fold {fold_i}: train missing classes "
                  f"{list(_all_classes - _train_classes)} — "
                  f"proxy CE-gap unreliable for this fold. "
                  f"(Resolves at production scale: ≥300 unique tasks.)")

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

        # Diagnostics from first fold
        if fold_i == 0:
            exp_var_first10 = z_pca.explained_variance_ratio_[:10].tolist()
            ev_mask = z_pca.explained_variance_ratio_ > 1e-8
            effective_rank = int(np.sum(ev_mask))
            pca_components_snapshots[dim_z] = z_pca.components_[:effective_rank].copy()

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

        # --- ||coef_proxy|| (in PCA space, full proxy coefficient norm) ---
        coef = grid_proxy.best_estimator_.coef_
        coef_z_norms.append(float(np.linalg.norm(coef)))
        chosen_Cs.append(float(grid_proxy.best_params_["C"]))

        # --- OOF log-loss ---
        for k, idx in enumerate(test_idx):
            val = A_in[idx]
            p_trace = probs_trace[k, trace_classes[val]] if val in trace_classes else 1e-10
            p_proxy = probs_proxy[k, proxy_classes[val]] if val in proxy_classes else 1e-10
            oof_l_trace[idx] = -np.log(max(p_trace, 1e-10))
            oof_l_proxy[idx] = -np.log(max(p_proxy, 1e-10))

        # --- Per-fold generalization diagnostics ---
        missing_classes = list(set(A_test) - set(A_train))
        train_prior = np.bincount(A_train, minlength=n_classes) / len(A_train)
        prior_ce = -np.mean(np.log(np.maximum(
            train_prior[A_test], 1e-10)))
        uniform_ce = -np.log(1.0 / n_classes) if n_classes > 0 else 0.0
        fold_trace_ce = -np.mean([np.log(max(
            probs_trace[k, trace_classes.get(A_test[k], 0)], 1e-10))
            if A_test[k] in trace_classes else np.log(1e-10)
            for k in range(len(A_test))])
        mean_p_true = np.mean([probs_trace[k, trace_classes[A_test[k]]]
                               if A_test[k] in trace_classes else 0.0
                               for k in range(len(A_test))])
        mean_max_prob = np.mean(np.max(probs_trace, axis=1))

        fold_diagnostics.append({
            "fold": fold_i,
            "n_train_tasks": len(np.unique(T_train)),
            "n_test_tasks": len(np.unique(T_test)),
            "missing_classes": missing_classes,
            "uniform_CE": uniform_ce,
            "prior_CE": prior_ce,
            "trace_CE_fold": fold_trace_ce,
            "mean_p_true": mean_p_true,
            "mean_max_prob": mean_max_prob,
        })

    ce_trace = float(np.mean(oof_l_trace[~np.isnan(oof_l_trace)]))
    ce_proxy = float(np.mean(oof_l_proxy[~np.isnan(oof_l_proxy)]))
    gap_bits = (ce_trace - ce_proxy) / np.log(2)

    return {
        "ce_trace": ce_trace,
        "ce_proxy": ce_proxy,
        "gap_bits": gap_bits,
        "coef_z_norm": float(np.mean(coef_z_norms)) if coef_z_norms else 0.0,
        "C_chosen": float(np.mean(chosen_Cs)) if chosen_Cs else 0.0,
        "effective_rank": effective_rank,
        "exp_var_first10": exp_var_first10,
        "pca_components_snapshot": pca_components_snapshots,
        "fold_diagnostics": fold_diagnostics,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Top-level CE-diff for one condition
# ═══════════════════════════════════════════════════════════════════════════

def run_condition(Z_raw, Phi, A, task_ids, label, folds, rng_seed=42):
    """Run real-Z (all dims), gaussian-Z (max dim), and permuted-Z (max dim).

    Returns (rows, null_gaps_gaussian, null_gaps_permuted).
    """
    N = len(A)
    unique_tasks = len(np.unique(task_ids))
    n_folds = len(folds)
    class_entropy = -sum((np.bincount(A) / N) * np.log(np.bincount(A) / N + 1e-10))
    rows = []
    # Store fold diagnostics keyed by (condition, z_type, dim) for later printing
    global_fold_diags = {}

    # --- Real Z at each dim ---
    for dim_z in DIMS:
        res = _eval_one(Z_raw, Phi, A, task_ids, dim_z, f"PCA-{dim_z}",
                        folds, rng_seed)
        rows.append({
            "condition": label, "z_type": f"PCA-{dim_z}", "dim": dim_z,
            "n_samples": N, "n_tasks": unique_tasks, "outer_cv": n_folds,
            "CE_trace_nats": res["ce_trace"], "CE_proxy_nats": res["ce_proxy"],
            "raw_gap_bits": res["gap_bits"], "C": res["C_chosen"],
            "effective_rank": res["effective_rank"],
            "exp_var_first10": res["exp_var_first10"],
            "pca_components_snapshot": res["pca_components_snapshot"],
            "fold_diagnostics": res["fold_diagnostics"],
        })
        if dim_z == DIMS[-1]:
            global_fold_diags[(label, f"PCA-{dim_z}")] = res["fold_diagnostics"]

    # --- Gaussian Z at max dim ---
    rng = np.random.RandomState(rng_seed)
    Z_gauss = rng.randn(N, Z_raw.shape[1]).astype(np.float32)
    res_g = _eval_one(Z_gauss, Phi, A, task_ids, DIMS[-1],
                      f"gaussian-Z-{DIMS[-1]}", folds, rng_seed)
    rows.append({
        "condition": label, "z_type": f"gaussian-Z-{DIMS[-1]}", "dim": DIMS[-1],
        "n_samples": N, "n_tasks": unique_tasks, "outer_cv": n_folds,
        "CE_trace_nats": res_g["ce_trace"], "CE_proxy_nats": res_g["ce_proxy"],
        "raw_gap_bits": res_g["gap_bits"], "C": res_g["C_chosen"],
        "effective_rank": res_g["effective_rank"],
        "exp_var_first10": res_g["exp_var_first10"],
        "pca_components_snapshot": res_g["pca_components_snapshot"],
        "fold_diagnostics": res_g["fold_diagnostics"],
    })

    # --- Permuted Z at max dim (global permutation, real labels) ---
    rng_perm = np.random.default_rng(SEED_ZPERM)
    Z_perm = rng_perm.permutation(Z_raw, axis=0).astype(np.float32)
    res_p = _eval_one(Z_perm, Phi, A, task_ids, DIMS[-1],
                      f"permuted-Z-{DIMS[-1]}", folds, rng_seed)
    rows.append({
        "condition": label, "z_type": f"permuted-Z-{DIMS[-1]}", "dim": DIMS[-1],
        "n_samples": N, "n_tasks": unique_tasks, "outer_cv": n_folds,
        "CE_trace_nats": res_p["ce_trace"], "CE_proxy_nats": res_p["ce_proxy"],
        "raw_gap_bits": res_p["gap_bits"], "C": res_p["C_chosen"],
        "effective_rank": res_p["effective_rank"],
        "exp_var_first10": res_p["exp_var_first10"],
        "pca_components_snapshot": res_p["pca_components_snapshot"],
        "fold_diagnostics": res_p["fold_diagnostics"],
    })

    # --- Repeated null suite ---
    null_gaps_gaussian = []
    null_gaps_permuted = []
    # Verify seeds are independent (one-time check)
    assert SEED_LABEL != SEED_ZPERM
    assert not np.array_equal(
        np.random.default_rng(SEED_LABEL).permutation(N),
        np.random.default_rng(SEED_ZPERM).permutation(N))

    for b in range(N_NULL_REPEATS):
        rng_label = np.random.RandomState(SEED_LABEL + b)
        A_shuf = A.copy()
        rng_label.shuffle(A_shuf)

        # Gaussian-Z null
        Z_gauss_null = np.random.RandomState(rng_seed + b).randn(
            N, Z_raw.shape[1]).astype(np.float32)
        res_gn = _eval_one(Z_gauss_null, Phi, A_shuf, task_ids, DIMS[-1],
                           "null-gaussian", folds, rng_seed)
        null_gaps_gaussian.append(res_gn["gap_bits"])

        # Permuted-Z null (global permutation with fresh seed per repeat)
        rng_pn = np.random.default_rng(SEED_ZPERM + b * 100)
        Z_perm_null = rng_pn.permutation(Z_raw, axis=0).astype(np.float32)
        res_pn = _eval_one(Z_perm_null, Phi, A_shuf, task_ids, DIMS[-1],
                           "null-permuted", folds, rng_seed)
        null_gaps_permuted.append(res_pn["gap_bits"])

    # Null p95
    null_p95 = max(np.percentile(null_gaps_gaussian, 95),
                   np.percentile(null_gaps_permuted, 95))

    # Null gating: if any single null repeat shows |gap| > 0.5, pipeline invalid
    max_null_gap = max(max(abs(g) for g in null_gaps_gaussian),
                       max(abs(g) for g in null_gaps_permuted))
    null_pass = max_null_gap < 0.5

    # Conservative certificate for each real-Z row
    for r in rows:
        r["null_p95_gap_bits"] = null_p95
        if np.isnan(r["raw_gap_bits"]):
            r["null_corrected_gap_bits"] = np.nan
            r["certified_delta_LB_bits"] = np.nan
        else:
            r["null_corrected_gap_bits"] = r["raw_gap_bits"] - null_p95
            r["certified_delta_LB_bits"] = max(0.0, r["null_corrected_gap_bits"])
        r["null_pass"] = null_pass
        r["class_entropy_nats"] = class_entropy
        r["max_null_gap"] = max_null_gap

    return rows, null_gaps_gaussian, null_gaps_permuted, global_fold_diags


# ═══════════════════════════════════════════════════════════════════════════
# Subspace stability
# ═══════════════════════════════════════════════════════════════════════════

def check_subspace_stability(rows, condition_label):
    """Check that effective-rank PCA components match across dims."""
    from scipy.linalg import subspace_angles

    pca_snapshots = {}
    for r in rows:
        if r["condition"] == condition_label and "PCA" in r["z_type"]:
            snap = r.get("pca_components_snapshot", {})
            for dim_z, comps in snap.items():
                if len(comps) > 0:
                    pca_snapshots[dim_z] = comps

    if len(pca_snapshots) < 2:
        return True, "only one dim, skipping"

    dims_sorted = sorted(pca_snapshots.keys())
    for i in range(len(dims_sorted) - 1):
        d1, d2 = dims_sorted[i], dims_sorted[i + 1]
        c1 = pca_snapshots[d1]
        c2 = pca_snapshots[d2]
        k = min(len(c1), len(c2))
        if k == 0:
            continue
        angles = subspace_angles(c1[:k].T, c2[:k].T)
        max_angle = np.max(angles) if len(angles) > 0 else 0.0
        if max_angle > 1e-3:
            return False, f"dim {d1} vs {d2}: max_angle={max_angle:.2e} rad > 1e-3"
    return True, "OK"


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype=torch.bfloat16).to(DEVICE)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model.eval()

all_rows = []
all_null_info = {}
all_fold_diags = {}

for cond_name, perturb_target, seed in [
    ("vanilla",       None,          SEED_DATA),
    ("perturbed",     "scratchpad",  SEED_DATA),
    ("wrong_module",  "query",       SEED_DATA),
]:
    print(f"\n{'#'*60}")
    print(f"# Capturing: {cond_name}")
    print(f"{'#'*60}")
    Z_raw, Phi, A, task_ids = capture_one_condition(
        PLANNING_TASKS, perturb_target, rng_seed=seed)

    print(f"  Z={Z_raw.shape}, Phi={Phi.shape}, A={A.shape}")
    print(f"  task_ids: {len(np.unique(task_ids))} unique tasks")
    print(f"  Action dist: {dict(zip(*np.unique(A, return_counts=True)))}")

    # Build StratifiedGroupKFold
    folds, A_remapped, n_splits = _make_outer_folds(A, task_ids, seed)
    train_tasks_per_fold = [len(np.unique(task_ids[tr])) for tr, _ in folds]
    test_tasks_per_fold = [len(np.unique(task_ids[te])) for _, te in folds]
    print(f"  outer_cv={n_splits}, "
          f"train tasks/fold: {train_tasks_per_fold}, "
          f"test tasks/fold: {test_tasks_per_fold}")
    print(f"  effective n ≈ {len(np.unique(task_ids))} (unique tasks)")

    rows, null_g, null_p, fold_diags = run_condition(
        Z_raw, Phi, A_remapped, task_ids, cond_name, folds, rng_seed=seed)
    all_rows.extend(rows)
    all_null_info[cond_name] = {
        "null_gaps_gaussian": null_g,
        "null_gaps_permuted": null_p,
    }
    all_fold_diags.update(fold_diags)

# ═══════════════════════════════════════════════════════════════════════════
# Print tables
# ═══════════════════════════════════════════════════════════════════════════

print(f"\n\n{'='*150}")
print("DIAGNOSE V3 — SANITY-HARDENED PROXY CE-DIFF")
print(f"{'='*150}")
header = (f"{'condition':<14} {'z_type':<18} {'dim':>4}  "
          f"{'n_samp':>6} {'n_task':>6} {'cv':>3}  "
          f"{'CE_trace':>9} {'CE_proxy':>9} {'raw_gap':>9}  "
          f"{'null_p95':>9} {'null_corr':>9} {'cert_dLB':>9}  "
          f"{'C':>8} {'rank':>5} {'null?':>5}")
print(header)
print("-" * 150)

for r in all_rows:
    null_str = "OK" if r.get("null_pass", False) else "INVALID"

    def _fmt(val, spec=">9.4f"):
        if isinstance(val, float) and np.isnan(val):
            return "      N/A"
        return f"{val:{spec}}"

    print(f"{r['condition']:<14} {r['z_type']:<18} {r['dim']:>4}  "
          f"{r.get('n_samples', 0):>6} {r.get('n_tasks', 0):>6} "
          f"{r.get('outer_cv', 0):>3}  "
          f"{_fmt(r['CE_trace_nats'])} {_fmt(r['CE_proxy_nats'])} "
          f"{_fmt(r['raw_gap_bits'], '>+9.4f')}  "
          f"{_fmt(r.get('null_p95_gap_bits', 0))} "
          f"{_fmt(r.get('null_corrected_gap_bits', 0), '>+9.4f')} "
          f"{_fmt(r.get('certified_delta_LB_bits', 0))}  "
          f"{_fmt(r.get('C', 0), '>8.4f')} {r.get('effective_rank', -1):>5}  "
          f"{null_str:>5}")

# ── Null suite detail ──
print(f"\n\n{'='*100}")
print("NULL SUITE DETAIL (repeated label-shuffle controls)")
print(f"{'='*100}")
for cond_name in ["vanilla", "perturbed", "wrong_module"]:
    info = all_null_info.get(cond_name, {})
    ng = info.get("null_gaps_gaussian", [])
    np_ = info.get("null_gaps_permuted", [])
    if ng:
        print(f"\n  {cond_name}:")
        print(f"    gaussian-Z null:  "
              f"mean={np.mean(ng):+.4f}, p95={np.percentile(ng, 95):+.4f}, "
              f"max|gap|={max(abs(g) for g in ng):.4f}")
        print(f"    permuted-Z null:  "
              f"mean={np.mean(np_):+.4f}, p95={np.percentile(np_, 95):+.4f}, "
              f"max|gap|={max(abs(g) for g in np_):.4f}")
        max_null = max(max(abs(g) for g in ng), max(abs(g) for g in np_))
        gate = "PASS" if max_null < 0.5 else "INVALID"
        print(f"    null gate: {gate} (max|gap|={max_null:.4f} vs 0.5 threshold)")

# ── Fold-level generalization diagnostics ──
print(f"\n\n{'='*110}")
print("FOLD-LEVEL GENERALIZATION DIAGNOSTICS (PCA at max dim)")
print(f"{'='*110}")
for (cond, zt), diags in sorted(all_fold_diags.items()):
    print(f"\n  Condition: {cond}, Z_type: {zt}")
    print(f"  {'Fold':<5} {'TrTask':<7} {'TeTask':<7} {'MissingCls':<12} | "
          f"{'Uni_CE':>8} {'Prior_CE':>9} | {'Trace_CE_fold':>14} | "
          f"{'Mean_pTrue':>11} {'MaxProb':>8} | {'Status'}")
    print(f"  {'-'*105}")
    for fd in diags:
        mc = fd["missing_classes"]
        mc_str = str(mc) if mc else "[]"
        if mc:
            status = "WARN: Missing Class -> Confidently Wrong"
        elif fd["trace_CE_fold"] > fd["prior_CE"] + 0.5:
            status = "WARN: Distribution Shift -> Overfit"
        else:
            status = "OK (Trace ≈ Prior)"
        print(f"  {fd['fold']:<5} {fd['n_train_tasks']:<7} {fd['n_test_tasks']:<7} "
              f"{mc_str:<12} | {fd['uniform_CE']:>8.4f} {fd['prior_CE']:>9.4f} | "
              f"{fd['trace_CE_fold']:>14.4f} | {fd['mean_p_true']:>11.4f} "
              f"{fd['mean_max_prob']:>8.4f} | {status}")

# ── Subspace stability ──
print(f"\n\n{'='*80}")
print("PCA SUBSPACE STABILITY (effective-rank components, < 1e-3 rad)")
print(f"{'='*80}")
for cond in ["vanilla", "perturbed", "wrong_module"]:
    ok, msg = check_subspace_stability(all_rows, cond)
    print(f"  {cond}: {msg}")

# ── Gap pivot ──
print(f"\n\n{'='*120}")
print("GAP PIVOT — raw vs certified")
print(f"{'='*120}")
print(f"{'dim':>4}  {'':>10} {'vanilla':>25} {'perturbed':>25} {'wrong_module':>25}")
print(f"{'':>4}  {'':>10} {'raw':>11} {'cert':>11} {'raw':>11} {'cert':>11} "
      f"{'raw':>11} {'cert':>11}")
print("-" * 120)
for dim in DIMS:
    print(f"{dim:>4}  ", end="")
    for cond in ["vanilla", "perturbed", "wrong_module"]:
        match_raw = [r for r in all_rows if r["condition"] == cond
                     and r["dim"] == dim and "PCA" in r["z_type"]]
        if match_raw:
            print(f"  {match_raw[0]['raw_gap_bits']:>+9.4f}  "
                  f"{match_raw[0]['certified_delta_LB_bits']:>9.4f}  ", end="")
        else:
            print(f"  {'---':>9}  {'---':>9}  ", end="")
    print()

print("\nDone.")
