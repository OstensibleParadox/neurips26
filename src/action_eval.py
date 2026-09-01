"""Task-level evaluation for balanced binary probes and discrete actions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import numpy as np

from src.discrete_actions import canonical_action, empirical_distribution, js_divergence
from src.utils.bootstrap import cluster_bootstrap_ci


@dataclass(frozen=True)
class ActionObservation:
    case_id: str
    arm: int
    action: Any

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id:
            raise ValueError("case_id is required")
        if not isinstance(self.arm, int) or isinstance(self.arm, bool) or self.arm not in (0, 1):
            raise ValueError("arm must be 0 or 1")
        if self.action is None:
            raise ValueError("action cannot be null")
        canonical_action(self.action)


def _group_balanced(
    observations: Iterable[ActionObservation],
    allowed_actions: Sequence[Any] | None = None,
) -> dict[str, dict[int, list[Any]]]:
    groups: dict[str, dict[int, list[Any]]] = defaultdict(lambda: {0: [], 1: []})
    allowed = (
        {canonical_action(action) for action in allowed_actions}
        if allowed_actions is not None
        else None
    )
    for observation in observations:
        if allowed is not None and canonical_action(observation.action) not in allowed:
            raise ValueError(f"unknown action in case {observation.case_id}")
        groups[observation.case_id][observation.arm].append(observation.action)
    if not groups:
        raise ValueError("no action observations were supplied")
    for case_id, arms in groups.items():
        if not arms[0] or not arms[1]:
            raise ValueError(f"case {case_id} is missing a probe arm")
        if len(arms[0]) != len(arms[1]):
            raise ValueError(f"case {case_id} has unequal repetitions across arms")
    return dict(groups)


def per_case_js_bits(
    observations: Iterable[ActionObservation],
    allowed_actions: Sequence[Any] | None = None,
) -> dict[str, float]:
    """Compute balanced-probe conditional JS separately for each task case."""

    groups = _group_balanced(observations, allowed_actions)
    return {
        case_id: js_divergence(
            empirical_distribution(arms[0]),
            empirical_distribution(arms[1]),
            units="bits",
        )
        for case_id, arms in sorted(groups.items())
    }


def _permuted_mean_js(
    groups: dict[str, dict[int, list[Any]]], rng: np.random.Generator
) -> float:
    values = []
    for arms in groups.values():
        k = len(arms[0])
        pooled = list(arms[0]) + list(arms[1])
        permutation = rng.permutation(len(pooled))
        arm0 = [pooled[index] for index in permutation[:k]]
        arm1 = [pooled[index] for index in permutation[k:]]
        values.append(
            js_divergence(
                empirical_distribution(arm0),
                empirical_distribution(arm1),
                units="bits",
            )
        )
    return float(np.mean(values))


def evaluate_balanced_actions(
    observations: Iterable[ActionObservation],
    *,
    allowed_actions: Sequence[Any] | None = None,
    n_bootstrap: int = 2000,
    n_permutations: int = 2000,
    seed: int = 0,
) -> dict[str, Any]:
    """Return task-block uncertainty and arm-label randomization calibration.

    The plug-in JS estimate is explicitly reported as an effect estimate, not a
    theorem-level lower certificate.  Under the recorded complete balanced
    assignment, the randomization p-value tests a sharp no-arm-effect null; it
    does not turn the bootstrap interval into a lower confidence bound on JS.
    """

    if n_bootstrap <= 0 or n_permutations <= 0:
        raise ValueError("bootstrap and permutation counts must be positive")
    observations = list(observations)
    groups = _group_balanced(observations, allowed_actions)
    values_by_case = per_case_js_bits(observations, allowed_actions)
    case_ids = np.asarray(sorted(values_by_case), dtype=object)
    values = np.asarray([values_by_case[case_id] for case_id in case_ids], dtype=float)
    point, ci_lo, ci_hi = cluster_bootstrap_ci(
        values,
        case_ids,
        statistic="mean",
        n=n_bootstrap,
        seed=seed,
    )
    rng = np.random.default_rng(seed + 1)
    null_values = np.asarray(
        [_permuted_mean_js(groups, rng) for _ in range(n_permutations)], dtype=float
    )
    p_value = float((1 + np.sum(null_values >= point)) / (n_permutations + 1))
    return {
        "reported_statistic": "mean_task_plugin_js_bits",
        "plugin_point_estimate_bits": point,
        "descriptive_task_bootstrap_p02_5_p97_5_bits": [ci_lo, ci_hi],
        "arm_label_randomization_p_value": p_value,
        "randomization_null": "complete balanced arm reassignment within each case",
        "null_randomization_p95_bits": float(np.percentile(null_values, 95)),
        "n_cases": int(len(case_ids)),
        "repetitions_per_arm": {
            case_id: len(groups[case_id][0]) for case_id in sorted(groups)
        },
        "per_case_js_bits": values_by_case,
        "certificate_warning": (
            "the percentile range describes resampling variability of a biased "
            "plug-in statistic; it is not a confidence interval for population "
            "JS or a finite-sample lower certificate. The randomization p-value "
            "is only a sharp-null test and cannot satisfy G5 without a separate bound"
        ),
    }
