"""diagnose_v2: CE-diff with per-fold PCA, label-shuffle control, full diagnostics.

Fixes PCA leakage: PCA is fit on Z_train only, then applied to Z_test within each fold.
Adds label-shuffle sanity check: shuffled A → gap should be ~0.
Prints per-dim: Z shape, rank, explained_var[:10], PCA hash stability check.
"""
from __future__ import annotations

import sys, hashlib, random, warnings
from pathlib import Path
import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold
from transformers import AutoModelForCausalLM, AutoTokenizer

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "7.3_intervention"))
from run_intervention import PLANNING_TASKS, build_prompt

TOOL_CLASSES = ["search", "calculator", "email", "calendar", "weather"]
DEVICE = "mps"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
N_SAMPLES = 200
DIMS = [16, 32, 64, 128]
PHI_PCA_DIM = 128
N_FOLDS = 5

# ── Model loading & data capture (reused from v1) ────────────────────
def capture_one_condition(task_pool, perturb_target, rng_seed=42):
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
    tasks = (task_pool * ((N_SAMPLES // len(task_pool)) + 1))[:N_SAMPLES]
    rng.shuffle(tasks)

    Z_list, Phi_list, A_list = [], [], []

    for task_text, scratchpad in tasks:
        if perturb_target == "scratchpad":
            scratchpad = _mask_tokens(scratchpad, fraction=0.3, rng=rng)
        elif perturb_target == "query":
            task_text = _mask_tokens(task_text, fraction=0.3, rng=rng)

        prompt = build_prompt(task_text, scratchpad)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(DEVICE)
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

    h1.remove()
    h2.remove()
    return (np.array(Z_list, dtype=np.float32),
            np.array(Phi_list, dtype=np.float32),
            np.array(A_list, dtype=int))

def _mask_tokens(text: str, fraction: float, rng: random.Random) -> str:
    tokens = text.split()
    n_mask = max(1, int(len(tokens) * fraction))
    indices = sorted(rng.sample(range(len(tokens)), n_mask))
    for i in indices:
        tokens[i] = "[MASK]"
    return " ".join(tokens)

# ── Corrected CE-diff (PCA per fold) ─────────────────────────────────
def ce_diff_corrected(Z_raw, Phi, A_orig, dims, label, rng_seed=42):
    """CE-diff with per-fold PCA. Returns list of result dicts.

    For each dim, also tests permuted-Z and gaussian-Z controls.
    """
    N = len(A_orig)
    unique_classes = np.unique(A_orig)
    n_classes = len(unique_classes)
    label_map = {orig: i for i, orig in enumerate(unique_classes)}
    A = np.array([label_map[a] for a in A_orig])

    # Create folds ONCE — same folds for trace and proxy, all dims
    min_count = min(np.bincount(A))
    n_splits = min(N_FOLDS, min_count) if min_count >= 2 else 2
    try:
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=rng_seed)
        folds = list(skf.split(np.zeros(N), A))
    except ValueError:
        from sklearn.model_selection import KFold
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=rng_seed)
        folds = list(kf.split(np.zeros(N)))

    class_entropy = -sum((np.bincount(A) / N) * np.log(np.bincount(A) / N + 1e-10))
    rows = []

    def _eval_one(Z_in, Phi, A, dim, z_desc, fold_pca_rng):
        """Core fold loop. Z_in is raw (pre-PCA). PCA fit per fold on train only."""
        oof_l_trace = np.zeros(N)
        oof_l_proxy = np.zeros(N)
        coef_z_norms = []
        chosen_Cs = []
        pca_hashes = []  # hash of first min(dim,16) PC components per fold
        ranks = []
        exp_var_first10 = []

        for fold_i, (train_idx, test_idx) in enumerate(folds):
            Phi_train, Phi_test = Phi[train_idx], Phi[test_idx]
            Z_train_raw, Z_test_raw = Z_in[train_idx], Z_in[test_idx]
            A_train, A_test = A[train_idx], A[test_idx]

            inner_cv = max(2, min(3, np.min(np.bincount(A_train))))

            # PCA fit on train ONLY, transform test — for both Z and Phi
            actual_dim_z = min(dim, len(train_idx), Z_train_raw.shape[1])
            pca_z = PCA(n_components=actual_dim_z, random_state=fold_pca_rng + fold_i)
            Z_train = pca_z.fit_transform(Z_train_raw).astype(np.float32)
            Z_test = pca_z.transform(Z_test_raw).astype(np.float32)

            actual_dim_phi = min(PHI_PCA_DIM, len(train_idx), Phi_train.shape[1])
            pca_phi = PCA(n_components=actual_dim_phi, random_state=fold_pca_rng + fold_i)
            Phi_train_pca = pca_phi.fit_transform(Phi_train).astype(np.float32)
            Phi_test_pca = pca_phi.transform(Phi_test).astype(np.float32)

            # Diagnostics (from first fold)
            if fold_i == 0:
                exp_var_first10 = pca_z.explained_variance_ratio_[:10].tolist()
                rank_z = np.linalg.matrix_rank(Z_train)
                pca_hash = hashlib.sha256(
                    pca_z.components_[:min(actual_dim_z, 16)].tobytes()
                ).hexdigest()[:12]
                pca_hashes.append(pca_hash)
                ranks.append(rank_z)

            # Trace-only model
            m_trace = LogisticRegressionCV(Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
                                           cv=inner_cv, max_iter=500, random_state=rng_seed)
            m_trace.fit(Phi_train_pca, A_train)
            probs_trace = m_trace.predict_proba(Phi_test_pca)

            # Proxy model
            X_train_p = np.concatenate([Phi_train_pca, Z_train], axis=1)
            X_test_p = np.concatenate([Phi_test_pca, Z_test], axis=1)
            m_proxy = LogisticRegressionCV(Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
                                           cv=inner_cv, max_iter=500, random_state=rng_seed)
            m_proxy.fit(X_train_p, A_train)
            probs_proxy = m_proxy.predict_proba(X_test_p)

            coef = m_proxy.coef_
            d_phi = Phi_train_pca.shape[1]
            coef_z = coef[:, d_phi:]
            coef_z_norms.append(float(np.linalg.norm(coef_z)))
            chosen_Cs.append(float(m_proxy.C_[0]))

            trace_classes = {c: i for i, c in enumerate(m_trace.classes_)}
            proxy_classes = {c: i for i, c in enumerate(m_proxy.classes_)}
            for k, idx in enumerate(test_idx):
                val = A[idx]
                p_trace = probs_trace[k, trace_classes[val]] if val in trace_classes else 1e-10
                p_proxy = probs_proxy[k, proxy_classes[val]] if val in proxy_classes else 1e-10
                oof_l_trace[idx] = -np.log(max(p_trace, 1e-10))
                oof_l_proxy[idx] = -np.log(max(p_proxy, 1e-10))

        ce_trace = float(np.mean(oof_l_trace))
        ce_proxy = float(np.mean(oof_l_proxy))
        gap_bits = (ce_trace - ce_proxy) / np.log(2)

        return {
            "condition": label, "z_type": z_desc, "dim": dim,
            "CE_trace_nats": ce_trace, "CE_proxy_nats": ce_proxy,
            "gap_bits": gap_bits,
            "||coef_Z||_2": float(np.mean(coef_z_norms)),
            "C_chosen": float(np.mean(chosen_Cs)),
            "class_entropy": class_entropy,
            "exp_var_first10": exp_var_first10,
            "rank_Z_train": ranks[0] if ranks else -1,
            "pca_hash_first16": pca_hashes[0] if pca_hashes else "",
        }

    rng = np.random.RandomState(rng_seed)

    for proxy_dim in dims:
        # Real Z
        rows.append(_eval_one(Z_raw, Phi, A, proxy_dim, f"PCA-{proxy_dim}", rng_seed))
        # label preservation check uses same rng per dim for reproducibility

    # Permuted-Z at max dim (same across dims since Z_raw doesn't change)
    Z_perm = Z_raw[rng.permutation(N)]
    rows.append(_eval_one(Z_perm, Phi, A, dims[-1], f"permuted-Z-{dims[-1]}", rng_seed))

    # Gaussian-Z at max dim
    Z_gauss = rng.randn(N, Z_raw.shape[1]).astype(np.float32)
    rows.append(_eval_one(Z_gauss, Phi, A, dims[-1], f"gaussian-Z-{dims[-1]}", rng_seed))

    return rows

# ── Main ─────────────────────────────────────────────────────────────
print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16).to(DEVICE)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model.eval()

all_rows = []

for cond_name, perturb_target, seed in [
    ("vanilla",       None,          42),
    ("perturbed",     "scratchpad",  42),
    ("wrong_module",  "query",       42),
]:
    print(f"\n{'#'*60}")
    print(f"# Capturing: {cond_name}")
    print(f"{'#'*60}")
    Z_raw, Phi, A = capture_one_condition(PLANNING_TASKS, perturb_target, rng_seed=seed)

    print(f"  Z={Z_raw.shape}, Phi={Phi.shape}, A={A.shape}")
    print(f"  Action dist: {dict(zip(*np.unique(A, return_counts=True)))}")
    z_hash = hashlib.sha256(Z_raw.tobytes()[:200]).hexdigest()[:12]
    phi_hash = hashlib.sha256(Phi.tobytes()[:200]).hexdigest()[:12]
    print(f"  Z_hash={z_hash}  Phi_hash={phi_hash}")

    # Real labels
    rows = ce_diff_corrected(Z_raw, Phi, A, DIMS, cond_name, rng_seed=seed)
    all_rows.extend(rows)

    # Label-shuffle control
    A_shuffled = A.copy()
    np.random.RandomState(seed).shuffle(A_shuffled)
    rows_shuf = ce_diff_corrected(Z_raw, Phi, A_shuffled, DIMS,
                                   f"{cond_name}_shufA", rng_seed=seed)
    all_rows.extend(rows_shuf)

# ── Print tables ─────────────────────────────────────────────────────
print(f"\n\n{'='*120}")
print("CORRECTED CE DECOMPOSITION (PCA per fold, no leakage)")
print(f"{'='*120}")
header = (f"{'condition':<18} {'z_type':<18} {'dim':>4}  "
          f"{'CE(A|Φ)':>10}  {'CE(A|Φ,Z)':>10}  {'gap_bits':>10}  "
          f"{'||coef_Z||':>10}  {'C':>8}  {'rank':>5}  {'pca_hash':>12}  "
          f"{'exp_var[:3]'}")
print(header)
print("-" * 120)

for r in all_rows:
    ev = r.get("exp_var_first10", [])
    ev_str = f"[{ev[0]:.3f}, {ev[1]:.3f}, {ev[2]:.3f}]" if len(ev) >= 3 else "[]"
    print(f"{r['condition']:<18} {r['z_type']:<18} {r['dim']:>4}  "
          f"{r['CE_trace_nats']:>10.6f}  {r['CE_proxy_nats']:>10.6f}  "
          f"{r['gap_bits']:>+10.4f}  {r['||coef_Z||_2']:>10.6f}  "
          f"{r['C_chosen']:>8.4f}  {r['rank_Z_train']:>5}  "
          f"{r.get('pca_hash_first16', ''):>12}  {ev_str}")

# ── Label-shuffle check ──
print(f"\n\n{'='*80}")
print("LABEL-SHUFFLE SANITY CHECK (gap should be ~0)")
print(f"{'='*80}")
print(f"Class entropy H(A) = {all_rows[0]['class_entropy']:.4f} nats")
shuf_rows = [r for r in all_rows if "_shufA" in r["condition"]]
for r in shuf_rows:
    gap_ok = "OK" if abs(r['gap_bits']) < 0.15 else "FAIL"
    print(f"  {r['condition']:<22} {r['z_type']:<18}  "
          f"CE_trace={r['CE_trace_nats']:.4f}  CE_proxy={r['CE_proxy_nats']:.4f}  "
          f"gap={r['gap_bits']:+.4f}  {gap_ok}")

# ── PCA hash stability: first 16 PCs should be identical across dims ──
print(f"\n\n{'='*80}")
print("PCA HASH STABILITY (first 16 PC components should match across dims)")
print(f"{'='*80}")
for cond in ["vanilla", "perturbed", "wrong_module"]:
    hashes = {}
    for r in all_rows:
        if r["condition"] == cond and "PCA" in r["z_type"]:
            hashes[r["dim"]] = r.get("pca_hash_first16", "")
    if len(set(hashes.values())) == 1:
        print(f"  {cond}: OK — all dims share PCA hash {list(hashes.values())[0]}")
    else:
        print(f"  {cond}: MISMATCH — {hashes}")

# ── Gap pivot ──
print(f"\n\n{'='*90}")
print("GAP PIVOT (corrected)")
print(f"{'='*90}")
for dim in DIMS:
    print(f"dim={dim:>4}  ", end="")
    for cond in ["vanilla", "perturbed", "wrong_module"]:
        match = [r for r in all_rows if r["condition"] == cond
                 and r["dim"] == dim and "PCA" in r["z_type"]]
        g = match[0]["gap_bits"] if match else float("nan")
        print(f"  {cond}: {g:+.4f}  ", end="")
    print()

print("\nDone.")
