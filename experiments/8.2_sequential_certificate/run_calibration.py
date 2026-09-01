#!/usr/bin/env python3
"""Monte Carlo calibration of null validity, power, and optional stopping."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.provenance import git_provenance

from eprocess import simulate_trial


def rejection_rate(
    *,
    alternative: bool,
    trials: int,
    rounds: int,
    rho: float,
    alpha: float,
    seed: int,
    adaptive: bool,
) -> tuple[float, float | None]:
    outcomes = [
        simulate_trial(
            alternative=alternative,
            rounds=rounds,
            rho=rho,
            alpha=alpha,
            seed=seed + index,
            adaptive=adaptive,
        )
        for index in range(trials)
    ]
    rejected = [outcome for outcome in outcomes if outcome["rejected"]]
    rate = len(rejected) / trials
    mean_stop = (
        float(np.mean([outcome["stop_round"] for outcome in rejected]))
        if rejected
        else None
    )
    return rate, mean_stop


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=1000)
    parser.add_argument("--rounds", type=int, default=250)
    parser.add_argument("--rho", type=float, default=0.1)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=8102)
    parser.add_argument("--adaptive", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/8.2_sequential_certificate/calibration.json"),
    )
    args = parser.parse_args()
    null_rate, null_stop = rejection_rate(
        alternative=False,
        trials=args.trials,
        rounds=args.rounds,
        rho=args.rho,
        alpha=args.alpha,
        seed=args.seed,
        adaptive=args.adaptive,
    )
    power, alt_stop = rejection_rate(
        alternative=True,
        trials=args.trials,
        rounds=args.rounds,
        rho=args.rho,
        alpha=args.alpha,
        seed=args.seed + 10_000_000,
        adaptive=args.adaptive,
    )
    payload = {
        "status": "calibration_only_not_gate_decision",
        "runner": "experiments/8.2_sequential_certificate/run_calibration.py",
        "design": "adaptive_full_support" if args.adaptive else "fixed_balanced",
        "trials": args.trials,
        "max_rounds": args.rounds,
        "rho": args.rho,
        "alpha": args.alpha,
        "seed": args.seed,
        "provenance": git_provenance(ROOT),
        "null_false_positive_rate": null_rate,
        "alternative_power": power,
        "mean_stopping_round_null_rejections": null_stop,
        "mean_stopping_round_alternative_rejections": alt_stop,
        "guarantee_scope": "exact conditional trace clamp with known design denominator",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
