#!/usr/bin/env python3
"""Write the exact TraceTwin checks and a passive held-out baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.provenance import git_provenance

from tracetwin import (
    analytic_values,
    clamped_joint,
    conditional_mutual_information,
    passive_holdout_auc,
    passive_joint,
    total_variation,
    visible_marginal,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=float, default=0.2)
    parser.add_argument("--rho", type=float, default=0.1)
    parser.add_argument("--n-passive", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=2027)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/8.1_tracetwin/calibration.json"),
    )
    args = parser.parse_args()

    passive_bypass = passive_joint("bypass", args.p, args.rho)
    passive_mediated = passive_joint("mediated", args.p, args.rho)
    clamp_bypass = clamped_joint("bypass", args.p, args.rho)
    clamp_mediated = clamped_joint("mediated", args.p, args.rho)
    payload = {
        "status": "calibration_only_not_gate_decision",
        "runner": "experiments/8.1_tracetwin/run_calibration.py",
        "parameters": {
            "p": args.p,
            "rho": args.rho,
            "n_passive_per_mechanism": args.n_passive,
            "seed": args.seed,
        },
        "provenance": git_provenance(ROOT),
        "analytic": analytic_values(args.p, args.rho),
        "computed": {
            "passive_visible_tv": total_variation(
                visible_marginal(passive_bypass),
                visible_marginal(passive_mediated),
            ),
            "passive_bypass_cmi_bits": conditional_mutual_information(passive_bypass),
            "passive_mediated_cmi_bits": conditional_mutual_information(passive_mediated),
            "clamped_bypass_cmi_bits": conditional_mutual_information(clamp_bypass),
            "clamped_mediated_cmi_bits": conditional_mutual_information(clamp_mediated),
            "passive_holdout_auc": passive_holdout_auc(
                args.p,
                args.rho,
                n_per_mechanism=args.n_passive,
                seed=args.seed,
            ),
        },
        "regime_warning": "passive and controlled-clamp CMI are different estimands",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["computed"]["passive_visible_tv"] > 1e-12:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
