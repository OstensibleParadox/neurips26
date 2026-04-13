#!/usr/bin/env python3
"""
compile_from_raw.py — Generic raw/ → compiled/ pipeline.

Usage:
    python compile_from_raw.py --experiment concordance --base_condition temperature=1.0
    python compile_from_raw.py --experiment format_robustness --base_condition format=direct

Auto-discovers all .jsonl files in raw/{experiment}/, groups by
(model, temperature|format, trial_id), computes Agency Index metrics,
and writes:
    compiled/{exp}_results.csv       — per (model, condition, trial)
    compiled/{exp}_stats.csv         — aggregated: mean, std, CI, eos_pct
    compiled/{exp}_results.csv.md5   — integrity checksum
    compiled/{exp}_stats.csv.md5     — integrity checksum
"""
import argparse
import csv
import gzip
import hashlib
import json
import sys
import warnings
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

# ── Repo root on sys.path ──────────────────────────────────────────────────────
REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.metrics import agency_index
from src.utils.bootstrap import bootstrap_ci


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_base_condition(base_cond: str) -> tuple[str, str]:
    """Parse 'key=value' string into (key, value)."""
    key, val = base_cond.split("=", 1)
    return key.strip(), val.strip()


def load_raw_records(raw_dir: Path) -> list[dict]:
    records = []
    jsonl_files = sorted(raw_dir.glob("*.jsonl"))
    if not jsonl_files:
        raise FileNotFoundError(f"No .jsonl files found in {raw_dir}")
    for jf in jsonl_files:
        with open(jf) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    warnings.warn(f"Skipping bad JSON in {jf}: {e}")
    return records


def group_records(records: list[dict], condition_key: str) -> dict:
    """Group records by (model_name, condition_value, trial_id)."""
    groups = defaultdict(list)
    for r in records:
        model = r.get("model_name", "unknown")
        cond  = str(r.get(condition_key, "unknown"))
        trial = r.get("trial_id", 0)
        groups[(model, cond, trial)].append(r)
    return groups


def compute_metrics_for_group(
    model_samples: list[dict],
    base_samples: list[dict],
    min_base: int = 10,
) -> dict | None:
    """Compute AI metrics for one (model, condition, trial) group."""
    texts_model = [r.get("generated_text", "") for r in model_samples]
    texts_base  = [r.get("generated_text", "") for r in base_samples]

    if len(texts_base) < min_base:
        return None

    # All-samples metrics
    m_all = agency_index(texts_model, texts_base)

    # EOS-clean metrics
    clean_model = [r.get("generated_text", "") for r in model_samples
                   if r.get("finish_reason", "stop") == "stop"]
    clean_base  = [r.get("generated_text", "") for r in base_samples
                   if r.get("finish_reason", "stop") == "stop"]

    m_clean = None
    if len(clean_model) >= 5 and len(clean_base) >= 5:
        m_clean = agency_index(clean_model, clean_base)

    eos_pct = sum(1 for r in model_samples
                  if r.get("finish_reason", "stop") == "length") / len(model_samples)
    n_clean = len(clean_model)
    output_len_mean = np.mean([r.get("n_tokens", 0) for r in model_samples])

    return {
        "ai":       m_all["ai"],
        "kl":       m_all["kl"],
        "mdl_mean": m_all["mdl_mean"],
        "mdl_std":  m_all["mdl_std"],
        "ai_clean": m_clean["ai"] if m_clean else float("nan"),
        "kl_clean": m_clean["kl"] if m_clean else float("nan"),
        "eos_pct":  eos_pct,
        "n_samples": len(model_samples),
        "n_clean":  n_clean,
        "output_len_mean": output_len_mean,
    }


def compile_experiment(
    experiment: str,
    base_condition: str,
    data_root: Path,
    min_base_n: int = 10,
):
    raw_dir     = data_root / "raw"     / experiment
    compiled_dir = data_root / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    print(f"[compile] {experiment} | base: {base_condition}")
    print(f"  raw:      {raw_dir}")
    print(f"  compiled: {compiled_dir}")

    records = load_raw_records(raw_dir)
    print(f"  loaded {len(records)} raw records")

    base_key, base_val = parse_base_condition(base_condition)
    condition_key = base_key  # the key used for grouping (e.g. "temperature" or "format")

    # Collect base samples: all records where base_key == base_val
    base_records_by_model = defaultdict(list)
    for r in records:
        if str(r.get(base_key, "")) == base_val:
            base_records_by_model[r.get("model_name", "unknown")].append(r)

    groups = group_records(records, condition_key)

    # Compute per-(model, condition, trial) metrics
    results_rows = []
    skipped = 0
    for (model, cond, trial), group_recs in sorted(groups.items()):
        base = base_records_by_model[model]
        if len(base) < min_base_n:
            warnings.warn(f"  [WARN] base n={len(base)} < {min_base_n} for {model} "
                          f"({base_condition}); skipping")
            skipped += 1
            continue
        m = compute_metrics_for_group(group_recs, base, min_base=min_base_n)
        if m is None:
            skipped += 1
            continue
        row = {
            "model":     model,
            condition_key: cond,
            "trial_id":  trial,
            **m,
        }
        results_rows.append(row)

    print(f"  computed {len(results_rows)} rows ({skipped} skipped)")

    # Write results CSV
    if not results_rows:
        print("  [ERROR] No results computed.")
        return

    results_path = compiled_dir / f"{experiment}_results.csv"
    fieldnames = list(results_rows[0].keys())
    with open(results_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(results_rows)

    # Aggregate into stats CSV
    stats_by_model_cond = defaultdict(list)
    for row in results_rows:
        key = (row["model"], row[condition_key])
        stats_by_model_cond[key].append(row)

    stats_rows = []
    for (model, cond), rows in sorted(stats_by_model_cond.items()):
        ai_vals    = [r["ai"]    for r in rows if not np.isnan(r["ai"])]
        ai_c_vals  = [r["ai_clean"] for r in rows if not np.isnan(r.get("ai_clean", float("nan")))]
        eos_vals   = [r["eos_pct"] for r in rows]
        n_clean_v  = [r["n_clean"] for r in rows]

        if not ai_vals:
            continue

        ci_lo, ci_hi = bootstrap_ci(ai_vals) if len(ai_vals) >= 3 else (float("nan"), float("nan"))

        stats_rows.append({
            "model":        model,
            condition_key:  cond,
            "n_trials":     len(rows),
            "ai_mean":      np.mean(ai_vals),
            "ai_std":       np.std(ai_vals),
            "ai_ci_lo":     ci_lo,
            "ai_ci_hi":     ci_hi,
            "ai_clean_mean": np.mean(ai_c_vals) if ai_c_vals else float("nan"),
            "eos_pct_mean": np.mean(eos_vals),
            "n_clean_mean": np.mean(n_clean_v),
        })

    stats_path = compiled_dir / f"{experiment}_stats.csv"
    if stats_rows:
        with open(stats_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(stats_rows[0].keys()))
            w.writeheader()
            w.writerows(stats_rows)

    # Write MD5 checksums
    for p in [results_path, stats_path]:
        if p.exists():
            cksum = md5_file(p)
            with open(f"{p}.md5", "w") as f:
                f.write(f"{cksum}  {p.name}\n")
            print(f"  [+] {p.name}  md5={cksum}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--experiment",      required=True,
                   help="Experiment name (subdirectory of raw/)")
    p.add_argument("--base_condition",  required=True,
                   help="'key=value' for base distribution (e.g. temperature=1.0)")
    p.add_argument("--data_root",       default=None,
                   help="Path to repo/data/ (default: auto-detect from script location)")
    p.add_argument("--min_base_n",      type=int, default=10,
                   help="Minimum base samples required (default: 10)")
    args = p.parse_args()

    if args.data_root:
        data_root = Path(args.data_root)
    else:
        data_root = REPO / "data"

    compile_experiment(
        experiment=args.experiment,
        base_condition=args.base_condition,
        data_root=data_root,
        min_base_n=args.min_base_n,
    )


if __name__ == "__main__":
    main()
