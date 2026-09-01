"""Exact TraceTwin distributions and finite-sample samplers."""

from __future__ import annotations

import math
from collections import Counter
from typing import Mapping

import numpy as np


Joint = dict[tuple[int, int, int], float]


def _check_parameters(p: float, rho: float) -> None:
    if not 0.0 < p <= 0.5:
        raise ValueError("p must satisfy 0 < p <= 1/2")
    if not 0.0 <= rho < 0.5:
        raise ValueError("rho must satisfy 0 <= rho < 1/2")


def binary_entropy(probability: float) -> float:
    """Binary entropy in bits."""

    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    if probability in (0.0, 1.0):
        return 0.0
    return -probability * math.log2(probability) - (1.0 - probability) * math.log2(
        1.0 - probability
    )


def crossover(p: float, rho: float) -> float:
    _check_parameters(p, rho)
    return p + rho - 2.0 * p * rho


def passive_joint(mechanism: str, p: float, rho: float) -> Joint:
    """Return the passive-label law P(Z,T,A)."""

    _check_parameters(p, rho)
    if mechanism not in {"bypass", "mediated"}:
        raise ValueError("mechanism must be 'bypass' or 'mediated'")
    r = crossover(p, rho)
    joint: Joint = {}
    for z in (0, 1):
        for t in (0, 1):
            p_t = (1.0 - p) if t == z else p
            for action in (0, 1):
                parent = z if mechanism == "bypass" else t
                error = rho if mechanism == "bypass" else r
                p_action = (1.0 - error) if action == parent else error
                joint[(z, t, action)] = 0.5 * p_t * p_action
    return joint


def clamped_joint(
    mechanism: str, p: float, rho: float, *, clamped_trace: int = 0
) -> Joint:
    """Return P(Z,T,A) after randomizing Z and imposing do(T=t)."""

    _check_parameters(p, rho)
    if mechanism not in {"bypass", "mediated"}:
        raise ValueError("mechanism must be 'bypass' or 'mediated'")
    if clamped_trace not in (0, 1):
        raise ValueError("clamped_trace must be binary")
    r = crossover(p, rho)
    joint: Joint = {}
    for z in (0, 1):
        for action in (0, 1):
            parent = z if mechanism == "bypass" else clamped_trace
            error = rho if mechanism == "bypass" else r
            p_action = (1.0 - error) if action == parent else error
            joint[(z, clamped_trace, action)] = 0.5 * p_action
    return joint


def visible_marginal(joint: Mapping[tuple[int, int, int], float]) -> dict[tuple[int, int], float]:
    marginal = {(t, action): 0.0 for t in (0, 1) for action in (0, 1)}
    for (_, t, action), probability in joint.items():
        marginal[(t, action)] += probability
    return marginal


def total_variation(
    p: Mapping[tuple[int, int], float], q: Mapping[tuple[int, int], float]
) -> float:
    support = set(p) | set(q)
    return 0.5 * sum(abs(p.get(key, 0.0) - q.get(key, 0.0)) for key in support)


def conditional_mutual_information(joint: Mapping[tuple[int, int, int], float]) -> float:
    """Compute I(Z;A|T) in bits from a finite joint law."""

    p_t: Counter[int] = Counter()
    p_zt: Counter[tuple[int, int]] = Counter()
    p_ta: Counter[tuple[int, int]] = Counter()
    for (z, t, action), probability in joint.items():
        p_t[t] += probability
        p_zt[(z, t)] += probability
        p_ta[(t, action)] += probability
    result = 0.0
    for (z, t, action), probability in joint.items():
        if probability == 0.0:
            continue
        ratio = probability * p_t[t] / (p_zt[(z, t)] * p_ta[(t, action)])
        result += probability * math.log2(ratio)
    return result


def analytic_values(p: float, rho: float) -> dict[str, float]:
    r = crossover(p, rho)
    return {
        "r": r,
        "passive_bypass_cmi_bits": binary_entropy(r) - binary_entropy(rho),
        "passive_mediated_cmi_bits": 0.0,
        "clamped_bypass_cmi_bits": 1.0 - binary_entropy(rho),
        "clamped_mediated_cmi_bits": 0.0,
    }


def sample_visible(
    mechanism: str, p: float, rho: float, n: int, seed: int
) -> np.ndarray:
    """Sample only (T,A), intentionally hiding Z from a passive baseline."""

    if n <= 0:
        raise ValueError("n must be positive")
    joint = passive_joint(mechanism, p, rho)
    outcomes = sorted(joint)
    probabilities = np.asarray([joint[outcome] for outcome in outcomes], dtype=float)
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(outcomes), size=n, p=probabilities)
    return np.asarray([(outcomes[index][1], outcomes[index][2]) for index in indices])


def passive_holdout_auc(
    p: float, rho: float, *, n_per_mechanism: int = 4000, seed: int = 0
) -> float:
    """Held-out saturated classifier AUC using only the four (T,A) cells."""

    if n_per_mechanism < 20:
        raise ValueError("n_per_mechanism must be at least 20")
    bypass = sample_visible("bypass", p, rho, n_per_mechanism, seed)
    mediated = sample_visible("mediated", p, rho, n_per_mechanism, seed + 1)
    split = n_per_mechanism // 2
    train = [(tuple(row), 1) for row in bypass[:split]] + [
        (tuple(row), 0) for row in mediated[:split]
    ]
    counts = {(t, a): [1.0, 1.0] for t in (0, 1) for a in (0, 1)}
    for cell, label in train:
        counts[cell][label] += 1.0
    scores = {
        cell: positive / (negative + positive)
        for cell, (negative, positive) in counts.items()
    }
    positive_scores = [scores[tuple(row)] for row in bypass[split:]]
    negative_scores = [scores[tuple(row)] for row in mediated[split:]]
    wins = 0.0
    for positive in positive_scores:
        for negative in negative_scores:
            wins += float(positive > negative) + 0.5 * float(positive == negative)
    return wins / (len(positive_scores) * len(negative_scores))
