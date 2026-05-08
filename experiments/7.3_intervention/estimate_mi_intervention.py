"""Intervention certificate estimation for §7.3.

Injects controlled perturbations ξ_hidden into hidden modules of a deployed
agent, holds the visible trace ~T_t fixed, and estimates
  I(ξ_hidden; A_t | ~T_t)
or the conditional JS divergence between perturbed and unperturbed action
distributions.

The experiment includes:
  - Dormant task (calculator-only): scratchpad unused → δ^LB ≈ 0
  - Active task (planning/search): scratchpad needed → δ^LB > 0
showing the two certificate axes are nonredundant.

Model: small open-weight LM (Qwen2.5-1.5B or similar) via HF transformers.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn


# ---------------------------------------------------------------------------
# Perturbation types
# ---------------------------------------------------------------------------

@dataclass
class PerturbationSpec:
    """Description of a perturbation to a hidden module."""
    target: str          # module name: "scratchpad", "router_cache", "memory_read"
    mode: str            # "gaussian", "mask", "replace", "dropout"
    strength: float      # σ for gaussian, mask_prob for mask/replace, drop_prob for dropout
    seed: int = 42


def apply_gaussian_noise(hidden: np.ndarray, sigma: float, rng: np.random.RandomState) -> np.ndarray:
    return hidden + sigma * rng.randn(*hidden.shape).astype(np.float32)


def apply_mask(hidden: np.ndarray, mask_prob: float, rng: np.random.RandomState) -> np.ndarray:
    mask = rng.rand(*hidden.shape) > mask_prob
    return hidden * mask.astype(np.float32)


def apply_perturbation(hidden: np.ndarray, spec: PerturbationSpec,
                       rng: np.random.RandomState | None = None) -> np.ndarray:
    if rng is None:
        rng = np.random.RandomState(spec.seed)
    if spec.mode == "gaussian":
        return apply_gaussian_noise(hidden, spec.strength, rng)
    elif spec.mode == "mask":
        return apply_mask(hidden, spec.strength, rng)
    elif spec.mode == "replace":
        replacement = rng.randn(*hidden.shape).astype(np.float32)
        mask = rng.rand(*hidden.shape) < spec.strength
        return np.where(mask, replacement, hidden)
    elif spec.mode == "dropout":
        mask = rng.rand(*hidden.shape) > spec.strength
        return (hidden * mask.astype(np.float32)) / max(1.0 - spec.strength, 0.01)
    else:
        raise ValueError(f"unknown perturbation mode: {spec.mode}")


# ---------------------------------------------------------------------------
# Conditional JS divergence estimation
# ---------------------------------------------------------------------------

def estimate_js_divergence(
    actions_wild: np.ndarray,
    actions_perturbed: np.ndarray,
    n_classes: int,
    n_bootstrap: int = 1000,
) -> dict:
    """Estimate JS(P_wild || P_perturbed) from action samples.

    For discrete action space, compute empirical distributions and JS.
    """
    def empirical_dist(actions, n_cls):
        counts = np.bincount(actions, minlength=n_cls)
        return counts / counts.sum()

    P = empirical_dist(actions_wild, n_classes)
    Q = empirical_dist(actions_perturbed, n_classes)
    M = 0.5 * (P + Q)

    def kl(a, b):
        # elementwise KL with safety
        mask = (a > 0) & (b > 0)
        return np.sum(np.where(mask, a * np.log(a / b), 0.0))

    js = 0.5 * kl(P, M) + 0.5 * kl(Q, M)

    # Bootstrap CI
    N = len(actions_wild)
    boot = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(N, N, replace=True)
        Pb = empirical_dist(actions_wild[idx], n_classes)
        Qb = empirical_dist(actions_perturbed[idx], n_classes)
        Mb = 0.5 * (Pb + Qb)
        boot.append(0.5 * kl(Pb, Mb) + 0.5 * kl(Qb, Mb))

    ci_lo, ci_hi = np.percentile(boot, 2.5), np.percentile(boot, 97.5)
    return {
        "estimator": "js_divergence",
        "js_divergence": float(js),
        "ci_95": [float(ci_lo), float(ci_hi)],
        "n_wild": int(len(actions_wild)),
        "n_perturbed": int(len(actions_perturbed)),
        "n_classes": n_classes,
    }


# ---------------------------------------------------------------------------
# Log-likelihood shift
# ---------------------------------------------------------------------------

def estimate_loglik_shift(
    loglik_wild: np.ndarray,
    loglik_perturbed: np.ndarray,
    n_bootstrap: int = 1000,
) -> dict:
    """Estimate mean log-likelihood shift from perturbation.

    Positive shift = perturbed actions are less likely under wild distribution.
    """
    shift = np.mean(loglik_wild - loglik_perturbed)
    boot = []
    N = len(loglik_wild)
    for _ in range(n_bootstrap):
        idx = np.random.choice(N, N, replace=True)
        boot.append(np.mean(loglik_wild[idx] - loglik_perturbed[idx]))
    ci_lo, ci_hi = np.percentile(boot, 2.5), np.percentile(boot, 97.5)
    return {
        "estimator": "loglik_shift",
        "mean_shift": float(shift),
        "ci_95": [float(ci_lo), float(ci_hi)],
        "n": N,
    }


# ---------------------------------------------------------------------------
# Intervention run record
# ---------------------------------------------------------------------------

@dataclass
class InterventionRun:
    task: str            # "calculator_only" or "planning_search"
    perturbation: PerturbationSpec | None  # None = wild (no perturbation)
    actions: list[int] = field(default_factory=list)
    logprobs: list[float] = field(default_factory=list)
    n_samples: int = 0

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "perturbation": {
                "target": self.perturbation.target if self.perturbation else "none",
                "mode": self.perturbation.mode if self.perturbation else "none",
                "strength": self.perturbation.strength if self.perturbation else 0.0,
            },
            "actions": self.actions,
            "logprobs": self.logprobs,
            "n_samples": self.n_samples,
        }


def run_intervention_experiment(
    runs: list[InterventionRun],
    out_path: str | Path,
) -> dict:
    """Compare wild vs perturbed runs per task, producing the dormant/active table."""
    # Group by task and perturbation
    from collections import defaultdict
    groups = defaultdict(list)
    for r in runs:
        key = (r.task, r.perturbation.target if r.perturbation else "wild")
        groups[key].append(r)

    results = {}
    for (task, target), run_list in groups.items():
        if target == "wild":
            continue
        wild_runs = [r for r in groups.get((task, "wild"), [])]
        if not wild_runs:
            continue

        wild_actions = np.concatenate([np.array(r.actions) for r in wild_runs])
        pert_actions_list = [np.array(r.actions) for r in run_list]
        if not pert_actions_list:
            continue
        pert_actions = np.concatenate(pert_actions_list)

        n_cls = int(max(wild_actions.max(), pert_actions.max())) + 1
        js_result = estimate_js_divergence(wild_actions, pert_actions, n_cls)

        wild_ll = np.concatenate([np.array(r.logprobs) for r in wild_runs])
        pert_ll = np.concatenate([np.array(r.logprobs) for r in run_list])
        ll_result = estimate_loglik_shift(wild_ll, pert_ll)

        results[f"{task}/{target}"] = {
            "task": task,
            "target": target,
            "js_divergence": js_result,
            "loglik_shift": ll_result,
            "n_wild": len(wild_actions),
            "n_perturbed": len(pert_actions),
        }

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=float)

    return results
