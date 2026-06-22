"""Replay certificate experiment for §7.2 replay class.

Controlled replay: the auditor holds the visible trace ~T_t fixed, varies
whether a missing state fragment (the hidden scratchpad) is reconstructed,
and measures the resulting action-distribution shift.

  Wild:   agent sees user query + hidden scratchpad -> A_t^wild
  Replay: agent sees user query only (no scratchpad)         -> A_t^replay
  ~T_t is identical in both conditions (the visible user query).

  JS(P_wild || P_replay | ~T_t) lower-bounds delta_act.

Also runs a reconstruction-fidelity sweep: 0% (empty), 25%, 50%, 75%, 100%
of scratchpad tokens retained.  JS should increase with fidelity.
"""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_intervention import (
    CALCULATOR_TASKS, PLANNING_TASKS, TOOL_TOKENS,
    build_prompt, load_config, InterventionConfig,
)


def get_action_distribution(model, tokenizer, prompt: str, device) -> np.ndarray:
    """Return empirical action distribution over tool tokens for one prompt."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True,
                      max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits[:, -1, :].cpu().float()

    tool_ids = []
    for tok in TOOL_TOKENS:
        ids = tokenizer.encode(tok, add_special_tokens=False)
        if ids:
            tool_ids.append(ids[0])

    probs = torch.softmax(logits[0, tool_ids], dim=-1).numpy()
    return probs


def get_action(logits: np.ndarray) -> int:
    return int(np.argmax(logits))


def reconstruct_scratchpad(scratchpad: str, fidelity: float,
                           rng: random.Random) -> str:
    """Reconstruct scratchpad at given fidelity.

    fidelity=0.0 -> empty (auditor knows nothing)
    fidelity=1.0 -> full scratchpad (perfect reconstruction = wild)
    """
    if fidelity >= 1.0:
        return scratchpad
    if fidelity <= 0.0:
        return "(no additional context available)"

    tokens = scratchpad.split()
    n_keep = max(1, int(len(tokens) * fidelity))
    kept_indices = sorted(rng.sample(range(len(tokens)), n_keep))
    return " ".join(tokens[i] for i in kept_indices)


def estimate_js(P_samples: list[np.ndarray],
                Q_samples: list[np.ndarray],
                n_bootstrap: int = 1000) -> dict:
    """Estimate JS divergence between two sets of action-distribution samples."""
    P = np.array(P_samples)
    Q = np.array(Q_samples)

    # Mean distributions
    P_mean = P.mean(axis=0)
    Q_mean = Q.mean(axis=0)
    M = 0.5 * (P_mean + Q_mean)

    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return float(np.sum(np.where(mask, a * np.log(a / b), 0.0)))

    js = 0.5 * kl(P_mean, M) + 0.5 * kl(Q_mean, M)

    # Bootstrap CI
    N = len(P)
    boot = []
    rng = np.random.RandomState(42)
    for _ in range(n_bootstrap):
        idx = rng.choice(N, N, replace=True)
        Pb = P[idx].mean(axis=0)
        Qb = Q[idx].mean(axis=0)
        Mb = 0.5 * (Pb + Qb)
        boot.append(0.5 * kl(Pb, Mb) + 0.5 * kl(Qb, Mb))
    ci_lo, ci_hi = np.percentile(boot, 2.5), np.percentile(boot, 97.5)

    return {
        "estimator": "js_divergence_mean_distributions",
        "js_divergence_nats": js,
        "js_divergence_bits": js / np.log(2),
        "ci_95_nats": [float(ci_lo), float(ci_hi)],
        "wild_mean_dist": P_mean.tolist(),
        "replay_mean_dist": Q_mean.tolist(),
        "n_wild": N,
        "n_replay": N,
    }


def run_replay_experiment(cfg: InterventionConfig) -> dict:
    """Run wild + replay with fidelity sweep."""
    device = torch.device(cfg.device)
    print(f"Loading {cfg.model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_name, torch_dtype=getattr(torch, cfg.dtype)
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model.eval()

    task_pool = CALCULATOR_TASKS if cfg.task == "calculator_only" else PLANNING_TASKS
    rng = random.Random(cfg.seed)

    tasks = (task_pool * ((cfg.n_samples // len(task_pool)) + 1))[:cfg.n_samples]
    rng.shuffle(tasks)

    # Wild: full scratchpad
    print(f"  Running {cfg.n_samples} wild episodes ({cfg.task})...")
    wild_dists = []
    wild_actions = []
    for i, (task_text, scratchpad) in enumerate(tasks):
        prompt = build_prompt(task_text, scratchpad)
        probs = get_action_distribution(model, tokenizer, prompt, device)
        wild_dists.append(probs)
        wild_actions.append(get_action(probs))
        if (i + 1) % 100 == 0:
            print(f"    wild: {i+1}/{cfg.n_samples}")

    # Fidelity sweep
    fidelities = [0.0, 0.25, 0.5, 0.75]
    results = {}

    for fidelity in fidelities:
        replay_dists = []
        replay_actions = []
        recon_rng = random.Random(cfg.seed + 1)

        for task_text, scratchpad in tasks:
            recon_sp = reconstruct_scratchpad(scratchpad, fidelity, recon_rng)
            prompt = build_prompt(task_text, recon_sp)
            probs = get_action_distribution(model, tokenizer, prompt, device)
            replay_dists.append(probs)
            replay_actions.append(get_action(probs))

        js_result = estimate_js(wild_dists, replay_dists)
        key = f"replay_fidelity_{fidelity}"
        results[key] = {
            "task": cfg.task,
            "fidelity": fidelity,
            **js_result,
            "wild_action_dist": dict(Counter(wild_actions)),
            "replay_action_dist": dict(Counter(replay_actions)),
        }
        print(f"    fidelity={fidelity:.2f}: JS={js_result['js_divergence_nats']:.4f} nats "
              f"[{js_result['ci_95_nats'][0]:.4f}, {js_result['ci_95_nats'][1]:.4f}]")

    # Also test "empty scratchpad" (explicit neutral text)
    neutral_scratchpad = "(no additional context is available for this query)"
    neutral_dists = []
    neutral_actions = []
    for task_text, _ in tasks:
        prompt = build_prompt(task_text, neutral_scratchpad)
        probs = get_action_distribution(model, tokenizer, prompt, device)
        neutral_dists.append(probs)
        neutral_actions.append(get_action(probs))

    js_neutral = estimate_js(wild_dists, neutral_dists)
    results["replay_empty"] = {
        "task": cfg.task,
        "fidelity": "empty",
        **js_neutral,
        "wild_action_dist": dict(Counter(wild_actions)),
        "replay_action_dist": dict(Counter(neutral_actions)),
    }
    print(f"    empty: JS={js_neutral['js_divergence_nats']:.4f} nats "
          f"[{js_neutral['ci_95_nats'][0]:.4f}, {js_neutral['ci_95_nats'][1]:.4f}]")

    return results


def run_dormant_active_replay(config_path: str) -> None:
    """Run replay on both task splits and save comparison."""
    cfg = load_config(config_path)

    print("=" * 60)
    print("DORMANT TASK (calculator) — scratchpad irrelevant")
    print("=" * 60)
    cfg_dormant = load_config(config_path)
    cfg_dormant.task = "calculator_only"
    dormant = run_replay_experiment(cfg_dormant)

    print()
    print("=" * 60)
    print("ACTIVE TASK (planning) — scratchpad drives behavior")
    print("=" * 60)
    cfg_active = load_config(config_path)
    cfg_active.task = "planning_search"
    active = run_replay_experiment(cfg_active)

    # Save combined
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    combined = {"dormant": dormant, "active": active}
    out_path = out_dir / "replay_certificate.json"
    with open(out_path, "w") as f:
        json.dump(combined, f, indent=2, default=float)

    # Printable summary
    print()
    print("=" * 60)
    print("REPLAY CERTIFICATE SUMMARY")
    print("=" * 60)
    for fidelity_key in ["replay_empty", "replay_fidelity_0.0", "replay_fidelity_0.5"]:
        d = dormant.get(fidelity_key, {})
        a = active.get(fidelity_key, {})
        d_js = d.get("js_divergence_nats", 0)
        a_js = a.get("js_divergence_nats", 0)
        d_ci = d.get("ci_95_nats", [0, 0])
        a_ci = a.get("ci_95_nats", [0, 0])
        print(f"  {fidelity_key}:")
        print(f"    dormant: JS={d_js:.4f} [{d_ci[0]:.4f}, {d_ci[1]:.4f}]")
        print(f"    active:  JS={a_js:.4f} [{a_ci[0]:.4f}, {a_ci[1]:.4f}]")

    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run_dormant_active_replay(args.config)
