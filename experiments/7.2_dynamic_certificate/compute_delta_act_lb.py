"""Aggregate estimator outputs into final delta_act^LB audit row.

Loads result JSONs from CE-diff and optionally InfoNCE/MINE estimators;
reports max as delta_act^LB (max of valid lower bounds is a valid lower bound).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def aggregate(estimator_results: list[dict], out_path: str | Path) -> dict[str, Any]:
    """Load estimator JSONs, take max, write audit row."""
    if not estimator_results:
        raise ValueError("at least one estimator result required")

    best = max(estimator_results, key=lambda r: r.get("delta_act_lb_nats", 0.0))
    result = {
        "delta_act_lb_nats": best["delta_act_lb_nats"],
        "delta_act_lb_source": best.get("estimator", "unknown"),
        "ci_95": best.get("ci_95", [None, None]),
        "n": best.get("n", 0),
        "estimators": estimator_results,
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", nargs="+", required=True,
                        help="one or more estimator result JSON files")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    results = []
    for path in args.results:
        with open(path) as f:
            results.append(json.load(f))
    result = aggregate(results, args.out)
    print(f"delta_act^LB = {result['delta_act_lb_nats']:.4f} nats "
          f"(source: {result['delta_act_lb_source']}, n={result['n']})")
