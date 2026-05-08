"""Dormant-vs-active intervention experiment for S7.3.

Runs intervention on two task splits, producing the key figure:
  calculator_only  -> delta^LB ~= 0  (scratchpad irrelevant, dormant hidden state)
  planning_search  -> delta^LB > 0   (scratchpad needed, active hidden state)

Proves the two certificate axes are nonredundant.
"""

from __future__ import annotations

import copy

from run_intervention import load_config, run_intervention_experiment


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)

    print("=" * 60)
    print("DORMANT TASK: calculator_only")
    print("=" * 60)
    cfg_dormant = copy.deepcopy(cfg)
    cfg_dormant.task = "calculator_only"
    dormant_results = run_intervention_experiment(cfg_dormant)

    print()
    print("=" * 60)
    print("ACTIVE TASK: planning_search")
    print("=" * 60)
    cfg_active = copy.deepcopy(cfg)
    cfg_active.task = "planning_search"
    active_results = run_intervention_experiment(cfg_active)

    # Report comparison
    print()
    print("=" * 60)
    print("COMPARISON: Dormant vs Active")
    print("=" * 60)
    for key in dormant_results:
        d_js = dormant_results[key]["js_divergence"]
        a_js = active_results.get(key, {}).get("js_divergence", 0)
        d_ci = dormant_results[key]["js_ci_95"]
        a_ci = active_results.get(key, {}).get("js_ci_95", [0, 0])
        print(f"  {key}")
        print(f"    dormant: JS={d_js:.4f} [{d_ci[0]:.4f}, {d_ci[1]:.4f}]")
        print(f"    active:  JS={a_js:.4f} [{a_ci[0]:.4f}, {a_ci[1]:.4f}]")
