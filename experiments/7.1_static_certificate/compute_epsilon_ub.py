"""Static certificate upper bound computation (§7.1).

Loads an architecture spec, applies per-edge capacity formulas, and returns
epsilon_state^UB in bits, together with the minimum cut that realises it.
Supports logging ablation: ``--log-override`` accepts a JSON dict mapping
edge ``"from->to"`` keys to boolean logged status, overriding the spec default.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from enumerate_cuts import ArchSpec, load_spec, enumerate_minimal_cuts, reach_unlogged_edges


@dataclass
class EpsilonUBResult:
    spec_name: str
    epsilon_ub_bits: float
    epsilon_nominal_bits: float
    min_cut: list[tuple[str, str]]
    min_cut_bits: float
    sum_reach_bits: float
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_name": self.spec_name,
            "epsilon_ub_bits": self.epsilon_ub_bits,
            "epsilon_nominal_bits": self.epsilon_nominal_bits,
            "min_cut": [f"{u}->{v}" for u, v in self.min_cut],
            "min_cut_bits": self.min_cut_bits,
            "sum_reach_bits": self.sum_reach_bits,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Capacity formulas
# ---------------------------------------------------------------------------

def c_e_context_window(edge: dict[str, Any], _from=None, _to=None) -> float:
    n = edge.get("n_tokens")
    v = edge.get("vocab_size")
    if n is None or v is None:
        raise ValueError("context_window requires n_tokens and vocab_size")
    return n * math.log2(v)


def c_e_quantized_activation(edge: dict[str, Any], _from=None, to_node=None) -> float:
    for src in (edge, to_node, _from):
        if src is None:
            continue
        d = src.get("dim")
        b = src.get("bits_per_dim")
        if d is not None and b is not None:
            return d * b
    raise ValueError("quantized_activation requires dim and bits_per_dim")


def c_e_diffusion_latent(edge, _from=None, to_node=None):
    return c_e_quantized_activation(edge, _from, to_node)


def c_e_gaussian_source(edge: dict[str, Any], _from=None, _to=None) -> float:
    sigma = edge.get("sigma")
    if sigma is None or sigma <= 0:
        raise ValueError("gaussian_source requires positive sigma")
    return 0.5 * math.log2(2 * math.pi * math.e * sigma * sigma)


def c_e_fixed(edge: dict[str, Any], _from=None, _to=None) -> float:
    bits = edge.get("c_e_bits")
    if bits is None:
        raise ValueError("fixed formula requires c_e_bits")
    return float(bits)


CAPACITY_FORMULAS = {
    "context_window": c_e_context_window,
    "quantized_activation": c_e_quantized_activation,
    "diffusion_latent": c_e_diffusion_latent,
    "gaussian_source": c_e_gaussian_source,
    "fixed": c_e_fixed,
}


def edge_capacity(spec: ArchSpec, edge: dict[str, Any], log_override: dict[str, bool] | None = None) -> float:
    """Resolve capacity of one edge. Returns 0 if edge is logged (or overridden to logged)."""
    from_id = edge["from"]
    to_id = edge["to"]
    edge_key = f"{from_id}->{to_id}"

    is_logged = edge.get("logged", False)
    if log_override is not None and edge_key in log_override:
        is_logged = log_override[edge_key]

    if is_logged:
        return 0.0

    # Check for explicit c_e_bits
    if "c_e_bits" in edge and "c_e_formula" not in edge:
        return float(edge["c_e_bits"])

    formula = edge.get("c_e_formula")
    if formula is None:
        raise ValueError(f"unlogged edge {edge_key} has no c_e_formula or c_e_bits")
    if formula not in CAPACITY_FORMULAS:
        raise ValueError(f"unknown c_e_formula: {formula}")

    node_by_id = {n["id"]: n for n in spec.nodes}
    return CAPACITY_FORMULAS[formula](
        edge,
        _from=node_by_id.get(from_id),
        to_node=node_by_id.get(to_id),
    )


def compute_epsilon_ub(spec: ArchSpec, epsilon_nominal_bits: float = 0.0,
                       log_override: dict[str, bool] | None = None) -> EpsilonUBResult:
    """Compute static certificate upper bound for ``spec``.

    Args:
        spec: architecture specification
        epsilon_nominal_bits: H(S_t | T_t), the nominal gap when full trace is available
        log_override: optional dict mapping "from->to" to bool, overriding logged status

    Returns:
        EpsilonUBResult with epsilon_ub_bits, min cut, and notes.
    """
    # Build edge capacity map
    edge_cap: dict[tuple[str, str], float] = {}
    for e in spec.edges:
        cap = edge_capacity(spec, e, log_override)
        key = (e["from"], e["to"])
        edge_cap[key] = cap

    cuts = enumerate_minimal_cuts(spec, log_override=log_override)

    notes: list[str] = []
    sum_reach = sum(edge_cap.get(e, 0.0) for e in reach_unlogged_edges(spec, log_override))

    if not cuts:
        notes.append("no unlogged paths from source to sink; epsilon^UB = epsilon_nominal")
        return EpsilonUBResult(
            spec_name=spec.name,
            epsilon_ub_bits=epsilon_nominal_bits,
            epsilon_nominal_bits=epsilon_nominal_bits,
            min_cut=[],
            min_cut_bits=0.0,
            sum_reach_bits=sum_reach,
            notes=notes,
        )

    # Score each cut by total capacity
    best_cut: list[tuple[str, str]] = []
    best_cut_bits = float("inf")
    for cut in cuts:
        cut_bits = sum(edge_cap.get(e, 0.0) for e in cut)
        if cut_bits < best_cut_bits:
            best_cut_bits = cut_bits
            best_cut = cut

    epsilon_ub = epsilon_nominal_bits + best_cut_bits
    notes.append(f"min-cut capacity = {best_cut_bits:.1f} bits")

    return EpsilonUBResult(
        spec_name=spec.name,
        epsilon_ub_bits=math.ceil(epsilon_ub),
        epsilon_nominal_bits=epsilon_nominal_bits,
        min_cut=best_cut,
        min_cut_bits=best_cut_bits,
        sum_reach_bits=sum_reach,
        notes=notes,
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: compute_epsilon_ub.py <spec.json> [--log-override '{\"a->b\": false}']")
        sys.exit(2)

    spec = load_spec(sys.argv[1])
    log_override = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--log-override":
        log_override = json.loads(sys.argv[3])

    result = compute_epsilon_ub(spec, log_override=log_override)
    print(json.dumps(result.to_dict(), indent=2))
