"""
Pilot orchestrator: run §6.4 format-intervention MI experiment
across 4 Qwen3.5 instructed model sizes via Ollama.

For each cell (model size):
  1. Safety inference  → safety_judgments_{model}.jsonl
  2. MI estimation     → certificate_{model}.json
  3. Asymmetry         → asymmetry_report_{model}.json

Outputs: outputs/pilot_scaling_summary.csv

Usage:
  python run_pilot_qwen35.py \
      --config anon/experiments/6.4_format_intervention/configs/qwen35_pilot.yaml \
      --n_pairs 11
"""

import sys
import csv
import json
import subprocess
import tempfile
import yaml
from pathlib import Path

REPO    = Path(__file__).parents[3]
EXP_DIR = Path(__file__).parent
OUT_DIR = EXP_DIR / "outputs"


def safe_name(tag: str) -> str:
    return tag.replace(":", "_").replace("/", "_")


def write_model_config(base: dict, model_tag: str, out_path: Path) -> None:
    s = safe_name(model_tag)
    rel = "anon/experiments/6.4_format_intervention/outputs"
    cfg = {
        "paths": {
            "compiled_pairs":       base["paths"]["compiled_pairs"],
            "content_embeddings":   base["paths"]["content_embeddings"],
            "safety_judgments":     f"{rel}/safety_judgments_{s}.jsonl",
            "certificate":          f"{rel}/certificate_{s}.json",
            "sanity":               f"{rel}/sanity_{s}.json",
            "contamination_report": f"{rel}/contamination_report_{s}.json",
            "asymmetry_report":     f"{rel}/asymmetry_report_{s}.json",
        },
        "models": {
            "safety_judge":    model_tag,
            "content_encoder": base["models"]["content_encoder"],
        },
        "estimator": base["estimator"],
        "inference":  base["inference"],
    }
    with open(out_path, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)


def run(cmd: list[str]) -> int:
    result = subprocess.run(cmd)
    return result.returncode


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",  required=True)
    parser.add_argument("--n_pairs", type=int, default=11)
    args = parser.parse_args()

    with open(REPO / args.config) as f:
        base = yaml.safe_load(f)

    models  = base["models"]["pilot"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        for model_tag in models:
            s = safe_name(model_tag)
            print(f"\n{'='*60}\nCell: {model_tag}\n{'='*60}")

            # Write per-model temp config
            cfg_path = tmp / f"cfg_{s}.yaml"
            write_model_config(base, model_tag, cfg_path)

            # ── Step 1: safety inference ──────────────────────────────
            rc = run([
                sys.executable,
                str(EXP_DIR / "run_safety_ollama.py"),
                "--config",  args.config,
                "--model",   model_tag,
                "--n_pairs", str(args.n_pairs),
            ])
            if rc != 0:
                print(f"[skip] inference failed for {model_tag}")
                continue

            # ── Step 2: MI estimation ─────────────────────────────────
            run([
                sys.executable,
                str(EXP_DIR / "estimate_mi_format.py"),
                "--config", str(cfg_path),
            ])

            # ── Step 3: asymmetry ─────────────────────────────────────
            run([
                sys.executable,
                str(EXP_DIR / "asymmetry_analysis.py"),
                "--config", str(cfg_path),
            ])

            # ── Collect ───────────────────────────────────────────────
            row: dict = {"model": model_tag}

            cert_path = OUT_DIR / f"certificate_{s}.json"
            if cert_path.exists():
                c = load_json(cert_path)
                ci = c.get("ci_95", [None, None])
                row.update({
                    "n_pairs":   c.get("n_pairs"),
                    "I_hat_nats": c.get("delta_format_lb_nats"),
                    "ci_lo":     ci[0],
                    "ci_hi":     ci[1],
                    "flip_rate": (c.get("sanity") or {}).get("flip_rate"),
                })
                row["active"] = ci[0] is not None and ci[0] > 0

            asym_path = OUT_DIR / f"asymmetry_report_{s}.json"
            if asym_path.exists():
                a = load_json(asym_path)
                row.update({
                    "asymmetry":   a.get("directional_asymmetry"),
                    "p_asymmetry": a.get("binomial_test_p"),
                })

            summary.append(row)

            # Quick cell summary
            i  = row.get("I_hat_nats")
            lo = row.get("ci_lo")
            hi = row.get("ci_hi")
            i_str = f"{i:.4f} [{lo:.3f}, {hi:.3f}]" if i is not None else "N/A"
            asym  = row.get("asymmetry")
            asym_str = f"{asym:+.3f}" if asym is not None else "N/A"
            status = "ACTIVE" if row.get("active") else "silent"
            print(f"  I_hat={i_str}  asym={asym_str}  [{status}]")

    # ── Write summary CSV ─────────────────────────────────────────────
    fields = ["model", "n_pairs", "I_hat_nats", "ci_lo", "ci_hi",
              "flip_rate", "asymmetry", "p_asymmetry", "active"]
    summary_path = OUT_DIR / "pilot_scaling_summary.csv"
    with open(summary_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(summary)

    # ── Print table ───────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PILOT SCALING SUMMARY")
    print(f"{'='*60}")
    print(f"{'Model':<22} {'I_hat':>8} {'CI_lo':>8} {'CI_hi':>8} "
          f"{'flip':>6} {'asym':>7} {'p':>7}  active")
    print("-" * 80)
    for row in summary:
        def fmt(v, w=8, d=4):
            return f"{v:{w}.{d}f}" if v is not None else f"{'N/A':>{w}}"
        print(
            f"{row['model']:<22}"
            f" {fmt(row.get('I_hat_nats'))}"
            f" {fmt(row.get('ci_lo'))}"
            f" {fmt(row.get('ci_hi'))}"
            f" {fmt(row.get('flip_rate'), 6, 3)}"
            f" {fmt(row.get('asymmetry'), 7, 3)}"
            f" {fmt(row.get('p_asymmetry'), 7, 3)}"
            f"  {'ACTIVE' if row.get('active') else 'silent'}"
        )

    print(f"\nSummary → {summary_path}")


if __name__ == "__main__":
    main()
