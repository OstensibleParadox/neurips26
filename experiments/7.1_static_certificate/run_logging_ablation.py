"""Logging ablation for static certificate (S7.1).

Varies the logging level across the deployment, recomputes epsilon_UB at each
level, and produces the ablation curve: epsilon_UB vs logging level.
"""

from __future__ import annotations

import json
from pathlib import Path

from compute_epsilon_ub import load_spec, compute_epsilon_ub, ArchSpec

# Logging levels generated dynamically from the spec's unlogged edges.
# Each level zeroes one class of unlogged channel, progressing from
# minimal instrumentation (output only) to full instrumentation.

def _generate_logging_levels(spec: ArchSpec) -> dict[str, dict[str, bool]]:
    """Generate incremental logging levels from the spec's actual unlogged edges."""
    unlogged = [e for e in spec.edges if not e.get("logged", False)]
    levels: dict[str, dict[str, bool]] = {"output_only": {}}

    # Group edges by target suffix (e.g., "_read->S_t", "_logits->S_t")
    groups: dict[str, list[str]] = {}
    for e in unlogged:
        key = f"{e['from']}->{e['to']}"
        # Group by the 'from' node prefix
        group = e["from"].split("_")[0] if "_" in e["from"] else e["from"]
        groups.setdefault(group, []).append(key)

    # Build cumulative levels
    cumulative: dict[str, bool] = {}
    for group_name, edge_keys in sorted(groups.items()):
        for key in edge_keys:
            cumulative[key] = True
        levels[f"+log_{group_name}"] = dict(cumulative)

    levels["full_instrumentation"] = cumulative
    return levels


def run_logging_ablation(spec_path: str, out_path: str,
                         epsilon_nominal: float = 0.0) -> list[dict]:
    spec = load_spec(spec_path)
    log_levels = _generate_logging_levels(spec)
    results = []

    for level_name, overrides in log_levels.items():
        result = compute_epsilon_ub(spec, epsilon_nominal_bits=epsilon_nominal,
                                   log_override=overrides)
        row = {
            "logging_level": level_name,
            "epsilon_ub_bits": result.epsilon_ub_bits,
            "min_cut_bits": result.min_cut_bits,
            "min_cut": [f"{u}->{v}" for u, v in result.min_cut],
            "sum_reach_bits": result.sum_reach_bits,
        }
        results.append(row)
        print(f"{level_name:25s}  eps^UB = {result.epsilon_ub_bits:>8.1f} bits  "
              f"min-cut = {result.min_cut}")

    # Monotonicity check
    eps_values = [r["epsilon_ub_bits"] for r in results]
    for i in range(1, len(eps_values)):
        if eps_values[i] > eps_values[i - 1]:
            print(f"WARNING: non-monotonic at {results[i]['logging_level']}: "
                  f"{eps_values[i-1]} -> {eps_values[i]}")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="path to architecture spec JSON")
    parser.add_argument("--out", default="data/processed/logging_ablation.json")
    parser.add_argument("--epsilon-nominal", type=float, default=0.0)
    args = parser.parse_args()
    run_logging_ablation(args.spec, args.out, args.epsilon_nominal)
