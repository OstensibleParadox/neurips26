"""End-to-end planning proxy certificate pipeline.

1. Generate planning proxy dataset (natural scratchpad generation)
2. Run inference with mid-layer proxy capture (layer 16 raw hidden state)
3. Run proxy ablation with regularized predictors

Usage:
  python run_proxy_planning.py --device mps --predictor both
  python run_proxy_planning.py --skip-generation --predictor logistic_l2
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS_DIR = REPO_ROOT / "experiments"


def step1_generate_data(device: str, n_queries: int, n_repeats: int,
                         out_dir: str) -> bool:
    """Generate planning proxy dataset. Skip if data already exists."""
    out_path = REPO_ROOT / out_dir
    if out_path.exists() and list(out_path.glob("planning_*.txt")):
        n_existing = len(list(out_path.glob("planning_*.txt")))
        print(f"[1/3] SKIP: {n_existing} planning proxy files already exist in {out_dir}")
        return True

    print(f"[1/3] Generating planning proxy dataset ({n_queries} queries × "
          f"{n_repeats} repeats)...")
    cmd = [
        sys.executable,
        str(EXPERIMENTS_DIR / "7.3_intervention" / "generate_planning_proxy_data.py"),
        "--model", "Qwen/Qwen2.5-7B-Instruct",
        "--device", device,
        "--n_queries", str(n_queries),
        "--n_repeats", str(n_repeats),
        "--out", str(out_path),
    ]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode == 0


def step2_run_inference(device: str, n_samples: int) -> bool:
    """Run inference with mid-layer proxy capture."""
    pairs_path = REPO_ROOT / "data" / "processed" / "probe_pairs_planning.pt"
    if pairs_path.exists():
        print(f"[2/3] SKIP: pairs file already exists at {pairs_path}")
        return True

    print("[2/3] Running inference with layer-16 raw hidden state proxy...")

    # Read config template and update device/n_samples
    config_path = EXPERIMENTS_DIR / "7.2_dynamic_certificate" / "configs" / "inference_planning_midlayer.yaml"

    cmd = [
        sys.executable,
        str(EXPERIMENTS_DIR / "7.2_dynamic_certificate" / "run_inference.py"),
        "--config", str(config_path),
    ]
    # Override device via config editing — simpler: just run as-is and let user
    # pre-set the device in config. For convenience, we patch the config.
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    cfg["model"]["device"] = device
    cfg["task"]["n_samples"] = n_samples
    tmp_config = REPO_ROOT / "data" / "processed" / "_tmp_inference_planning.yaml"
    tmp_config.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_config, "w") as f:
        yaml.dump(cfg, f)

    cmd = [
        sys.executable,
        str(EXPERIMENTS_DIR / "7.2_dynamic_certificate" / "run_inference.py"),
        "--config", str(tmp_config),
    ]
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode == 0


def step3_run_ablation(predictor: str) -> bool:
    """Run proxy ablation with specified predictor(s)."""
    pairs_path = REPO_ROOT / "data" / "processed" / "probe_pairs_planning.pt"
    meta_path = REPO_ROOT / "data" / "processed" / "probe_meta_planning.json"

    if not pairs_path.exists():
        print(f"[3/3] ERROR: pairs file not found at {pairs_path}")
        return False

    predictors = ["logistic_l2", "mlp"] if predictor == "both" else [predictor]
    all_ok = True

    for pred in predictors:
        print(f"\n[3/3] Running proxy ablation with predictor={pred}...")
        out_path = REPO_ROOT / "data" / "processed" / f"proxy_ablation_planning_{pred}.json"

        cmd = [
            sys.executable,
            str(EXPERIMENTS_DIR / "7.2_dynamic_certificate" / "run_proxy_ablation.py"),
            "--pairs", str(pairs_path),
            "--meta", str(meta_path),
            "--predictor", pred,
            "--out", str(out_path),
        ]
        result = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if result.returncode != 0:
            all_ok = False
        else:
            _print_best_result(out_path)

    return all_ok


def _print_best_result(result_path: Path) -> None:
    """Print the best non-control result from an ablation JSON."""
    with open(result_path) as f:
        data = json.load(f)

    details = data.get("details", {})
    valid = {k: v for k, v in details.items()
             if k not in ("random", "permuted")
             and v.get("delta_act_lb_nats", -1) > 0}

    print(f"\n  Results for {result_path.stem}:")
    for k, v in details.items():
        bits = v.get("delta_act_lb_bits", 0)
        ci = v.get("ci_95_bits", [0, 0])
        print(f"    {k:12s}  {bits:.6f} bits  [{ci[0]:.6f}, {ci[1]:.6f}]")

    if valid:
        best_k = max(valid, key=lambda k: valid[k]["delta_act_lb_bits"])
        best_bits = valid[best_k]["delta_act_lb_bits"]
        print(f"  => BEST: {best_k} = {best_bits:.4f} bits")

        # Compare to old 0.0317 bits
        old = 0.0317
        improvement = best_bits / old if old > 0 else float("inf")
        print(f"  => vs old 0.0317 bits: {improvement:.1f}x improvement")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cpu",
                        choices=["cpu", "cuda", "mps"],
                        help="Device for model inference")
    parser.add_argument("--n-queries", type=int, default=50,
                        help="Number of unique planning queries")
    parser.add_argument("--n-repeats", type=int, default=20,
                        help="Repeats per query (total = n_queries × n_repeats)")
    parser.add_argument("--predictor", default="both",
                        choices=["logistic_l2", "mlp", "both"],
                        help="Predictor type for CE-diff")
    parser.add_argument("--skip-generation", action="store_true",
                        help="Skip data generation step")
    parser.add_argument("--skip-inference", action="store_true",
                        help="Skip inference step")
    args = parser.parse_args()

    n_total = args.n_queries * args.n_repeats
    print(f"Planning Proxy Certificate Pipeline")
    print(f"  Queries: {args.n_queries}, Repeats: {args.n_repeats}, "
          f"Total: {n_total}")
    print(f"  Device: {args.device}, Predictor: {args.predictor}")
    print()

    ok = True

    if not args.skip_generation:
        ok &= step1_generate_data(args.device, args.n_queries,
                                  args.n_repeats, "data/proxy_planning")

    if ok and not args.skip_inference:
        ok &= step2_run_inference(args.device, n_total)

    if ok:
        ok &= step3_run_ablation(args.predictor)

    if ok:
        print("\nDone. Pipeline complete.")
    else:
        print("\nPipeline failed — check errors above.")
        sys.exit(1)
