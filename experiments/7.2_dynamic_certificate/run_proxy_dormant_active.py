"""Proxy certificate with dormant/active task split — mirrors intervention §7.3.

Uses the intervention experiment's CALCULATOR_TASKS (dormant, scratchpad irrelevant)
and PLANNING_TASKS (active, scratchpad drives behavior) to show that the proxy
certificate detects behavioral activation in the same way as intervention/replay.

Design:
  - Same topology (scratchpad present in both) → same epsilon_UB
  - Different tasks → different delta_LB (proxy CE-diff)
  - Proves nonredundancy of the two certificate axes using proxy class

Usage:
  python run_proxy_dormant_active.py --device mps --predictor logistic_l2
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegressionCV
from transformers import AutoModelForCausalLM, AutoTokenizer

# Import task definitions from intervention experiment
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "7.3_intervention"))
from run_intervention import (
    CALCULATOR_TASKS, PLANNING_TASKS, TOOL_TOKENS,
    build_prompt, PerturbationSpec, perturb_scratchpad,
)
from run_replay import reconstruct_scratchpad

TOOL_CLASSES = ["search", "calculator", "email", "calendar", "weather"]


def capture_proxy_pairs(model, tokenizer, device, task_pool, n_samples,
                        perturb: bool = False, rng_seed: int = 42):
    """Capture (Z_t, Phi_t, A_t) for a task pool.

    Returns Z (raw layer-16 last-token hidden), Phi (layer-4 mean-pooled), A.
    """
    import random

    # Hooks
    trace_hidden = None
    probe_hidden = None

    def _unwrap_hs(output):
        if isinstance(output, tuple):
            return output[0].detach()
        return output.detach()

    def trace_hook(module, input, output):
        nonlocal trace_hidden
        trace_hidden = _unwrap_hs(output)

    def probe_hook(module, input, output):
        nonlocal probe_hidden
        probe_hidden = _unwrap_hs(output)

    trace_module = model.model.layers[4]
    probe_module = model.model.layers[16]
    h1 = trace_module.register_forward_hook(trace_hook)
    h2 = probe_module.register_forward_hook(probe_hook)

    rng = random.Random(rng_seed)
    tasks = (task_pool * ((n_samples // len(task_pool)) + 1))[:n_samples]
    rng.shuffle(tasks)

    Z_list, Phi_list, A_list = [], [], []

    for task_text, scratchpad in tasks:
        if perturb:
            spec = PerturbationSpec(target="scratchpad", mode="mask",
                                    strength=0.3, seed=rng.randint(0, 10000))
            scratchpad = perturb_scratchpad(scratchpad, spec, rng)

        prompt = build_prompt(task_text, scratchpad)
        inputs = tokenizer(prompt, return_tensors="pt",
                           truncation=True, max_length=512).to(device)
        with torch.no_grad():
            outputs = model(**inputs)

        if trace_hidden is None or probe_hidden is None:
            continue

        phi_t = trace_hidden.mean(dim=1).cpu().numpy().flatten()
        z_t = probe_hidden[:, -1, :].cpu().numpy().flatten()

        # Get action from full model logits (NOT lm_head on intermediate hidden)
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


def ce_diff_estimate(Phi, Z, A, predictor_type="logistic_l2"):
    """Cross-fitted CE-diff (same as run_proxy_ablation)."""
    from sklearn.model_selection import StratifiedKFold

    N = len(A)
    unique_classes = np.unique(A)
    num_classes = len(unique_classes)

    if num_classes < 2:
        return {"delta_act_lb_nats": 0.0, "delta_act_lb_bits": 0.0,
                "ci_95_bits": [0.0, 0.0], "n": N, "n_classes": num_classes,
                "note": "single class — no MI possible, trivially zero"}

    # Remap non-contiguous labels to 0..(num_classes-1)
    label_map = {orig: i for i, orig in enumerate(unique_classes)}
    A_remapped = np.array([label_map[a] for a in A])

    # Use 5-fold, handle classes with <5 members by using min(count, 5) folds
    min_count = min(np.bincount(A_remapped))
    n_splits = min(5, min_count) if min_count >= 2 else 2

    try:
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        folds = list(skf.split(np.zeros(N), A_remapped))
    except ValueError:
        from sklearn.model_selection import KFold
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        folds = list(kf.split(np.zeros(N)))

    oof_l_trace = np.zeros(N)
    oof_l_proxy = np.zeros(N)

    for train_idx, test_idx in folds:
        Phi_train, Phi_test = Phi[train_idx], Phi[test_idx]
        Z_train, Z_test = Z[train_idx], Z[test_idx]
        A_train, A_test = A_remapped[train_idx], A_remapped[test_idx]

        if predictor_type == "logistic_l2":
            m_trace = LogisticRegressionCV(Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
                                           max_iter=2000, random_state=42)
            m_proxy = LogisticRegressionCV(Cs=[0.001, 0.01, 0.1, 1.0, 10.0],
                                           max_iter=2000, random_state=42)
        else:
            from sklearn.neural_network import MLPClassifier
            m_trace = MLPClassifier(hidden_layer_sizes=(128,), alpha=0.01,
                                    early_stopping=True, random_state=42)
            m_proxy = MLPClassifier(hidden_layer_sizes=(128,), alpha=0.01,
                                    early_stopping=True, random_state=42)

        m_trace.fit(Phi_train, A_train)
        probs_trace = m_trace.predict_proba(Phi_test)

        X_train_p = np.concatenate([Phi_train, Z_train], axis=1)
        X_test_p = np.concatenate([Phi_test, Z_test], axis=1)
        m_proxy.fit(X_train_p, A_train)
        probs_proxy = m_proxy.predict_proba(X_test_p)

        for k, idx in enumerate(test_idx):
            val = A_remapped[idx]
            oof_l_trace[idx] = -np.log(max(probs_trace[k, val], 1e-10))
            oof_l_proxy[idx] = -np.log(max(probs_proxy[k, val], 1e-10))

    delta = float(np.mean(oof_l_trace) - np.mean(oof_l_proxy))

    # Bootstrap CI
    sample_mi = oof_l_trace - oof_l_proxy
    boot = []
    rng = np.random.RandomState(42)
    for _ in range(1000):
        idx = rng.choice(N, N, replace=True)
        boot.append(float(np.mean(sample_mi[idx])))
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

    return {
        "delta_act_lb_nats": delta,
        "delta_act_lb_bits": delta / np.log(2),
        "ci_95_bits": [float(ci_lo) / np.log(2), float(ci_hi) / np.log(2)],
        "n": N,
        "n_classes": num_classes,
    }


def run_dormant_active(model_name: str, dtype: str, device: str,
                       n_samples: int, predictor: str,
                       proxy_dim: int = 64) -> dict:
    """Run proxy certificate on both dormant and active task splits."""
    dev = torch.device(device)
    print(f"Loading {model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=getattr(torch, dtype)
    ).to(dev)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model.eval()

    results = {}

    # --- DORMANT (calculator) ---
    print(f"\n{'='*60}")
    print(f"DORMANT TASK (calculator) — scratchpad irrelevant")
    print(f"{'='*60}")
    Z_calc, Phi_calc, A_calc = capture_proxy_pairs(
        model, tokenizer, dev, CALCULATOR_TASKS, n_samples, perturb=False)

    print(f"  Captured {len(A_calc)} samples, {len(np.unique(A_calc))} classes")
    print(f"  Action distribution: {dict(zip(*np.unique(A_calc, return_counts=True)))}")

    # PCA
    if Z_calc.shape[1] > proxy_dim:
        pca = PCA(n_components=proxy_dim, random_state=42)
        Z_calc_pca = pca.fit_transform(Z_calc).astype(np.float32)
    else:
        Z_calc_pca = Z_calc

    # Trace-only predictor should already be perfect (all same action)
    result_calc = ce_diff_estimate(Phi_calc, Z_calc_pca, A_calc, predictor)
    print(f"  CE-diff: {result_calc['delta_act_lb_bits']:.4f} bits "
          f"[{result_calc['ci_95_bits'][0]:.4f}, {result_calc['ci_95_bits'][1]:.4f}]")
    results["calculator_dormant"] = result_calc

    # --- ACTIVE (planning) ---
    print(f"\n{'='*60}")
    print(f"ACTIVE TASK (planning) — scratchpad drives behavior")
    print(f"{'='*60}")
    Z_plan, Phi_plan, A_plan = capture_proxy_pairs(
        model, tokenizer, dev, PLANNING_TASKS, n_samples, perturb=False)

    print(f"  Captured {len(A_plan)} samples, {len(np.unique(A_plan))} classes")
    print(f"  Action distribution: {dict(zip(*np.unique(A_plan, return_counts=True)))}")

    if Z_plan.shape[1] > proxy_dim:
        pca = PCA(n_components=proxy_dim, random_state=42)
        Z_plan_pca = pca.fit_transform(Z_plan).astype(np.float32)
    else:
        Z_plan_pca = Z_plan

    result_plan = ce_diff_estimate(Phi_plan, Z_plan_pca, A_plan, predictor)
    print(f"  CE-diff: {result_plan['delta_act_lb_bits']:.4f} bits "
          f"[{result_plan['ci_95_bits'][0]:.4f}, {result_plan['ci_95_bits'][1]:.4f}]")
    results["planning_active"] = result_plan

    # Also: perturbed proxy for planning (adds more Z variation)
    print(f"\n{'='*60}")
    print(f"ACTIVE TASK with perturbations — more Z variation")
    print(f"{'='*60}")
    Z_pert, Phi_pert, A_pert = capture_proxy_pairs(
        model, tokenizer, dev, PLANNING_TASKS, n_samples, perturb=True)

    print(f"  Captured {len(A_pert)} samples, {len(np.unique(A_pert))} classes")
    print(f"  Action distribution: {dict(zip(*np.unique(A_pert, return_counts=True)))}")

    if Z_pert.shape[1] > proxy_dim:
        Z_pert_pca = pca.fit_transform(Z_pert).astype(np.float32)
    else:
        Z_pert_pca = Z_pert

    result_pert = ce_diff_estimate(Phi_pert, Z_pert_pca, A_pert, predictor)
    print(f"  CE-diff: {result_pert['delta_act_lb_bits']:.4f} bits "
          f"[{result_pert['ci_95_bits'][0]:.4f}, {result_pert['ci_95_bits'][1]:.4f}]")
    results["planning_perturbed"] = result_pert

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY: Proxy Certificate — Dormant vs Active")
    print(f"{'='*60}")
    print(f"  dormant (calculator):    {results['calculator_dormant']['delta_act_lb_bits']:.4f} bits")
    print(f"  active (planning):       {results['planning_active']['delta_act_lb_bits']:.4f} bits")
    print(f"  active+perturbed:        {results['planning_perturbed']['delta_act_lb_bits']:.4f} bits")

    # Save
    out_path = Path("data/processed/proxy_dormant_active.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"\nSaved to {out_path}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--dtype", default="float32")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--n-samples", type=int, default=200)
    parser.add_argument("--predictor", default="logistic_l2")
    parser.add_argument("--proxy-dim", type=int, default=64)
    args = parser.parse_args()

    run_dormant_active(args.model, args.dtype, args.device,
                       args.n_samples, args.predictor, args.proxy_dim)
