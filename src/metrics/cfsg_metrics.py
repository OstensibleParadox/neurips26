"""
CFSG metrics for multi-judge cross-validation (Section 6.1 upgrade).

All metrics are pure functions operating on scalars or numpy arrays.
Matches the formal Definition 4 (def:fcg) in the paper:
    CFSG(x, e1, e2) = |R(e1) - R(e2)| * (1 - d_repr(h_B(e1), h_B(e2)))
"""
import numpy as np


def score_gap(r_i: float, r_j: float) -> float:
    """Absolute reward-score difference |R(f_i(x)) - R(f_j(x))|."""
    return abs(r_i - r_j)


def local_slope(delta: float, d_repr: float, eta: float = 1e-6) -> float:
    """Empirical Lipschitz slope: delta / (d_repr + eta).

    Large values indicate non-Lipschitz behavior — the judge changes its
    score significantly despite small representation distance.
    """
    return delta / (d_repr + eta)


def full_cfsg(r_i: float, r_j: float, d_repr: float) -> float:
    """Formal CFSG from Definition 4: |R(e1) - R(e2)| * (1 - d_repr).

    The (1 - d_repr) term weights by representation similarity: when
    encodings are representationally close (d_repr ~ 0), the full CFSG
    equals the raw score gap. When far apart (d_repr ~ 1), the CFSG
    is attenuated — the formats are genuinely different to the model.
    """
    return abs(r_i - r_j) * (1.0 - d_repr)


def violation_rate(
    deltas: np.ndarray,
    d_reprs: np.ndarray,
    rho: float,
    tau: float,
) -> float:
    """Small-distance violation rate V_g(rho, tau).

    V_g = Pr(delta > tau | d_repr <= rho)

    Measures the fraction of representationally-close format pairs
    where the judge still exhibits non-trivial score drift.
    """
    mask = d_reprs <= rho
    if mask.sum() == 0:
        return float("nan")
    return float((deltas[mask] > tau).mean())


def pairwise_bias(p_ij: float) -> float:
    """Pairwise preference bias: |p_ij - 0.5|.

    For a format-insensitive pairwise judge, p_ij should be ~0.5.
    """
    return abs(p_ij - 0.5)


def pairwise_violation_rate(
    p_ijs: np.ndarray,
    d_reprs: np.ndarray,
    rho: float,
    gamma: float,
) -> float:
    """Pairwise small-distance violation rate W(rho, gamma).

    W = Pr(|p_ij - 0.5| > gamma | d_repr <= rho)

    Measures how often the pairwise judge shows format preference
    among representationally-close pairs.
    """
    mask = d_reprs <= rho
    if mask.sum() == 0:
        return float("nan")
    biases = np.abs(p_ijs[mask] - 0.5)
    return float((biases > gamma).mean())
