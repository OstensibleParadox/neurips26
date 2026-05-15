"""Diagnostic: CE decomposition + controls for proxy dimension sweep.

Conditions:
  vanilla       — standard scratchpad, Z from layer 16
  perturbed     — 30% mask on scratchpad tokens
  wrong_module  — 30% mask on USER QUERY (control: gap should NOT move)
  random_Z      — permuted Z (control: if monotonic trend persists, it's an artifact)
  gaussian_Z    — N(0,1) Z (control: even stronger artifact test)

For each condition × proxy_dim: CE(A|Phi), CE(A|Phi,Z), gap, ||coef_Z||_2.
"""
from __future__ import annotations

import sys, json, hashlib, random
from pathlib import Path
import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "7.3_intervention"))
from run_intervention import PLANNING_TASKS, TOOL_TOKENS, build_prompt

TOOL_CLASSES = ["search", "calculator", "email", "calendar", "weather"]
DEVICE = "mps"
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
N_SAMPLES = 200
DIMS = [16, 32, 64, 128]

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16).to(DEVICE)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model.eval()

# ── helpers ──────────────────────────────────────────────────────────
def capture_one_condition(task_pool, perturb_target, rng_seed=42):
    """Capture Z, Phi, A for one condition.

    perturb_target: None | "scratchpad" | "query"
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
    tasks = (task_pool * ((N_SAMPLES // len(task_pool)) + 1))[:N_SAMPLES]
    rng.shuffle(tasks)

    Z_list, Phi_list, A_list = [], [], []

    for task_text, scratchpad in tasks:
        # Apply perturbation to the specified target
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
    """Mask `fraction` of whitespace-delimited tokens in `text`."""
    tokens = text.split()
    n_mask = max(1, int(len(tokens) * fraction))
    indices = sorted(rng.sample(range(len(tokens)), n_mask))
    for i in indices:
        tokens[i] = "[MASK]"
    return " ".join(tokens)


def compute_ce_table(Z_raw, Phi, A, dims, label):
    """For a given (Z_raw, Phi, A), compute CE decomposition at each dim.

    Also computes random_Z and gaussian_Z controls using the FIRST dim's Z.
    Returns list of dicts.
    """
    N = len(A)
    unique_classes = np.unique(A)
    label_map = {orig: i for i, orig in enumerate(unique_classes)}
    A_remapped = np.array([label_map[a] for a in A])

    min_count = min(np.bincount(A_remapped))
    n_splits = min(5, min_count) if min_count >= 2 else 2
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    folds = list(skf.split(np.zeros(N), A_remapped))

    rows = []

    for proxy_dim in dims:
        # ── real Z (PCA) ──
        pca = PCA(n_components=proxy_dim, random_state=42)
        Z = pca.fit_transform(Z_raw).astype(np.float32)
        row = _ce_decompose(Phi, Z, A_remapped, folds, proxy_dim, label,
                            f"PCA-{proxy_dim}")
        rows.append(row)

    # ── random_Z control (permuted) at max dim ──
    pca = PCA(n_components=dims[-1], random_state=42)
    Z_full = pca.fit_transform(Z_raw).astype(np.float32)
    Z_perm = Z_full[np.random.RandomState(42).permutation(N)]
    row = _ce_decompose(Phi, Z_perm, A_remapped, folds, dims[-1], label,
                        f"permuted-Z-{dims[-1]}")
    rows.append(row)

    # ── gaussian_Z control at max dim ──
    Z_gauss = np.random.RandomState(42).randn(N, dims[-1]).astype(np.float32)
    row = _ce_decompose(Phi, Z_gauss, A_remapped, folds, dims[-1], label,
                        f"gaussian-Z-{dims[-1]}")
    rows.append(row)

    return rows


def _ce_decompose(Phi, Z, A_remapped, folds, proxy_dim, label, z_desc):
    """Core CE decomposition for one (Phi, Z, A) triple."""
    oof_l_trace = np.zeros(len(A_remapped))
    oof_l_proxy = np.zeros(len(A_remapped))
    coef_z_norms = []

    for train_idx, test_idx in folds:
        Phi_train, Phi_test = Phi[train_idx], Phi[test_idx]
        Z_train, Z_test = Z[train_idx], Z[test_idx]
        A_train, A_test = A_remapped[train_idx], A_remapped[test_idx]

        m_trace = LogisticRegressionCV(Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
                                       max_iter=2000, random_state=42)
        m_proxy = LogisticRegressionCV(Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
                                       max_iter=2000, random_state=42)

        m_trace.fit(Phi_train, A_train)
        probs_trace = m_trace.predict_proba(Phi_test)

        X_train_p = np.concatenate([Phi_train, Z_train], axis=1)
        X_test_p = np.concatenate([Phi_test, Z_test], axis=1)
        m_proxy.fit(X_train_p, A_train)
        probs_proxy = m_proxy.predict_proba(X_test_p)

        coef = m_proxy.coef_
        d_phi = Phi_train.shape[1]
        coef_z = coef[:, d_phi:]
        coef_z_norms.append(float(np.linalg.norm(coef_z)))

        for k, idx in enumerate(test_idx):
            val = A_remapped[idx]
            oof_l_trace[idx] = -np.log(max(probs_trace[k, val], 1e-10))
            oof_l_proxy[idx] = -np.log(max(probs_proxy[k, val], 1e-10))

    ce_trace = float(np.mean(oof_l_trace))
    ce_proxy = float(np.mean(oof_l_proxy))
    gap_bits = (ce_trace - ce_proxy) / np.log(2)
    avg_coef_norm = float(np.mean(coef_z_norms))

    return {
        "condition": label,
        "z_type": z_desc,
        "dim": proxy_dim,
        "CE_trace_nats": ce_trace,
        "CE_proxy_nats": ce_proxy,
        "gap_bits": gap_bits,
        "||coef_Z||_2": avg_coef_norm,
    }


# ── Main ─────────────────────────────────────────────────────────────
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
    # data integrity check
    z_hash = hashlib.sha256(Z_raw.tobytes()[:200]).hexdigest()[:12]
    phi_hash = hashlib.sha256(Phi.tobytes()[:200]).hexdigest()[:12]
    print(f"  Z_hash={z_hash}  Phi_hash={phi_hash}")

    rows = compute_ce_table(Z_raw, Phi, A, DIMS, cond_name)
    all_rows.extend(rows)

# ── Print table ──────────────────────────────────────────────────────
print(f"\n\n{'='*110}")
print("FULL CE DECOMPOSITION TABLE")
print(f"{'='*110}")
header = f"{'condition':<14} {'z_type':<18} {'dim':>4}  {'CE(A|Φ)':>10}  {'CE(A|Φ,Z)':>10}  {'gap_bits':>10}  {'||coef_Z||':>10}"
print(header)
print("-" * 110)

for r in all_rows:
    print(f"{r['condition']:<14} {r['z_type']:<18} {r['dim']:>4}  "
          f"{r['CE_trace_nats']:>10.6f}  {r['CE_proxy_nats']:>10.6f}  "
          f"{r['gap_bits']:>10.4f}  {r['||coef_Z||_2']:>10.6f}")

# ── Pivot: dim × condition gap comparison ──
print(f"\n\n{'='*80}")
print("GAP PIVOT: dim × condition")
print(f"{'='*80}")
conditions = ["vanilla", "perturbed", "wrong_module"]
print(f"{'dim':<6}", end="")
for c in conditions:
    print(f"  {c:<14}", end="")
print("  perturbed-vanilla  perturbed-wrong")
print("-" * 90)

for dim in DIMS:
    print(f"{dim:<6}", end="")
    gaps = {}
    for c in conditions:
        match = [r for r in all_rows if r['condition'] == c and r['dim'] == dim]
        g = match[0]['gap_bits'] if match else float('nan')
        gaps[c] = g
        print(f"  {g:>+10.4f} bits", end="")
    pv = gaps.get('perturbed', 0) - gaps.get('vanilla', 0)
    pw = gaps.get('perturbed', 0) - gaps.get('wrong_module', 0)
    print(f"  {pv:>+14.4f}      {pw:>+13.4f}")

# ── Random-Z diagnostics ──
print(f"\n\n{'='*80}")
print("CONTROL: Random-Z vs Real-Z at dim={}".format(DIMS[-1]))
print(f"{'='*80}")
for r in all_rows:
    if r['dim'] == DIMS[-1]:
        print(f"  {r['z_type']:<22}  gap={r['gap_bits']:>+10.4f}  "
              f"||coef_Z||={r['||coef_Z||_2']:>10.6f}  "
              f"CE_trace={r['CE_trace_nats']:>10.6f}  CE_proxy={r['CE_proxy_nats']:>10.6f}")

print("\nDone.")
