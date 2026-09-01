"""Anytime-valid evidence for exact-clamp binary audit rounds."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


def _probability_vector(values: Sequence[float], name: str) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or len(vector) < 2:
        raise ValueError(f"{name} must be a one-dimensional probability vector")
    if np.any(~np.isfinite(vector)) or np.any(vector <= 0.0):
        raise ValueError(f"{name} must have full support")
    if not math.isclose(float(vector.sum()), 1.0, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(f"{name} must sum to one")
    return vector


@dataclass
class EvidenceProcess:
    """Track e-capital and its Ville anytime p-value."""

    alpha: float = 0.05
    log_e_value: float = 0.0
    max_log_e_value: float = 0.0
    rounds: int = 0

    def __post_init__(self) -> None:
        if not 0.0 < self.alpha < 1.0:
            raise ValueError("alpha must lie in (0,1)")

    def update(
        self,
        observed_probe: int,
        decoder_distribution: Sequence[float],
        design_distribution: Sequence[float],
    ) -> float:
        """Consume a decoder chosen before fitting the current labeled row."""

        decoder = _probability_vector(decoder_distribution, "decoder_distribution")
        design = _probability_vector(design_distribution, "design_distribution")
        if len(decoder) != len(design):
            raise ValueError("decoder and design alphabets differ")
        if not 0 <= observed_probe < len(design):
            raise ValueError("observed_probe is outside the design alphabet")
        factor = float(decoder[observed_probe] / design[observed_probe])
        self.log_e_value += math.log(factor)
        self.max_log_e_value = max(self.max_log_e_value, self.log_e_value)
        self.rounds += 1
        return factor

    @property
    def e_value(self) -> float:
        return math.exp(self.log_e_value)

    @property
    def anytime_p_value(self) -> float:
        return min(1.0, math.exp(-self.max_log_e_value))

    @property
    def rejected(self) -> bool:
        return self.max_log_e_value >= math.log(1.0 / self.alpha)


@dataclass
class OnlineActionDecoder:
    """A prequential categorical decoder with Dirichlet smoothing."""

    n_probes: int = 2
    prior: float = 0.5
    counts: dict[str, np.ndarray] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.n_probes < 2 or self.prior <= 0.0:
            raise ValueError("n_probes >= 2 and prior > 0 are required")

    def predict(self, action: str) -> np.ndarray:
        """Return g_i before the current (action, probe) row is fitted."""

        counts = self.counts.get(str(action))
        if counts is None:
            counts = np.full(self.n_probes, self.prior, dtype=float)
        return counts / counts.sum()

    def fit_observation(self, action: str, probe: int) -> None:
        if not 0 <= probe < self.n_probes:
            raise ValueError("probe is outside the decoder alphabet")
        key = str(action)
        if key not in self.counts:
            self.counts[key] = np.full(self.n_probes, self.prior, dtype=float)
        self.counts[key][probe] += 1.0


def adaptive_design(round_index: int, previous_action: int | None) -> np.ndarray:
    """A predictable, full-support policy used by the calibration suite."""

    if previous_action is None:
        return np.asarray([0.5, 0.5])
    probability_one = 0.65 if previous_action == (round_index % 2) else 0.35
    return np.asarray([1.0 - probability_one, probability_one])


def simulate_trial(
    *,
    alternative: bool,
    rounds: int,
    rho: float,
    alpha: float,
    seed: int,
    adaptive: bool,
) -> dict[str, float | int | bool]:
    """Simulate a null or binary-bypass sequence with optional stopping."""

    if rounds <= 0:
        raise ValueError("rounds must be positive")
    if not 0.0 <= rho < 0.5:
        raise ValueError("rho must lie in [0,1/2)")
    rng = np.random.default_rng(seed)
    decoder = OnlineActionDecoder()
    evidence = EvidenceProcess(alpha=alpha)
    previous_action: int | None = None
    stop_round = rounds
    for round_index in range(rounds):
        design = (
            adaptive_design(round_index, previous_action)
            if adaptive
            else np.asarray([0.5, 0.5])
        )
        probe = int(rng.choice(2, p=design))
        if alternative:
            action = probe ^ int(rng.random() < rho)
        else:
            action = int(rng.random() < 0.5)
        decoder_distribution = decoder.predict(str(action))
        evidence.update(probe, decoder_distribution, design)
        decoder.fit_observation(str(action), probe)
        previous_action = action
        if evidence.rejected:
            stop_round = round_index + 1
            break
    return {
        "rejected": evidence.rejected,
        "stop_round": stop_round,
        "rounds_observed": evidence.rounds,
        "e_value": evidence.e_value,
        "anytime_p_value": evidence.anytime_p_value,
    }
