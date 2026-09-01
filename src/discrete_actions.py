"""Shared metrics for finite, safety-relevant action alphabets.

The v2 experiments deliberately evaluate structured deployed actions rather
than token logits or neural mutual-information proxies.  This module contains
the small, dependency-light pieces that are shared by TraceTwin and the real
action-boundary evaluation.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any, Iterable, Mapping, Sequence


def canonical_action(action: Any) -> str:
    """Return a stable label for a JSON-compatible structured action."""

    return json.dumps(
        action,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def empirical_distribution(actions: Iterable[Any]) -> dict[str, float]:
    """Estimate a categorical distribution over canonical action labels."""

    labels = [canonical_action(action) for action in actions]
    if not labels:
        raise ValueError("at least one action is required")
    counts = Counter(labels)
    total = float(len(labels))
    return {label: count / total for label, count in sorted(counts.items())}


def _aligned(
    p: Mapping[str, float], q: Mapping[str, float]
) -> tuple[list[float], list[float]]:
    support = sorted(set(p) | set(q))
    p_values = [float(p.get(key, 0.0)) for key in support]
    q_values = [float(q.get(key, 0.0)) for key in support]
    _validate_probabilities(p_values, "p")
    _validate_probabilities(q_values, "q")
    return p_values, q_values


def _validate_probabilities(values: Sequence[float], name: str) -> None:
    if not values:
        raise ValueError(f"{name} has empty support")
    if any(not math.isfinite(value) or value < 0.0 for value in values):
        raise ValueError(f"{name} contains an invalid probability")
    if not math.isclose(sum(values), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"{name} must sum to one")


def total_variation(
    p: Mapping[str, float], q: Mapping[str, float]
) -> float:
    """Total-variation distance between two finite action laws."""

    p_values, q_values = _aligned(p, q)
    return 0.5 * sum(abs(pi - qi) for pi, qi in zip(p_values, q_values))


def kl_divergence(
    p: Mapping[str, float],
    q: Mapping[str, float],
    *,
    units: str = "nats",
) -> float:
    """KL(p || q), returning infinity on a support violation."""

    p_values, q_values = _aligned(p, q)
    value = 0.0
    for pi, qi in zip(p_values, q_values):
        if pi == 0.0:
            continue
        if qi == 0.0:
            return math.inf
        value += pi * math.log(pi / qi)
    if units == "bits":
        return value / math.log(2.0)
    if units != "nats":
        raise ValueError("units must be 'nats' or 'bits'")
    return value


def js_divergence(
    p: Mapping[str, float],
    q: Mapping[str, float],
    *,
    units: str = "bits",
) -> float:
    """Jensen--Shannon divergence on a common finite support."""

    p_values, q_values = _aligned(p, q)
    support = [str(index) for index in range(len(p_values))]
    p_aligned = dict(zip(support, p_values))
    q_aligned = dict(zip(support, q_values))
    midpoint = {
        key: 0.5 * (p_aligned[key] + q_aligned[key]) for key in support
    }
    return 0.5 * kl_divergence(p_aligned, midpoint, units=units) + 0.5 * kl_divergence(
        q_aligned, midpoint, units=units
    )
