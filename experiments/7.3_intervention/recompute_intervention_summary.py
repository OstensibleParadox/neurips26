"""Recompute ReAct intervention summaries from per-sample raw JSONL.

The raw files are produced by ``run_intervention.py`` and contain one row per
task sample and condition, including the argmax action and the full tool-choice
probability vector.  This script rebuilds the checked-in aggregate JSON/CSV
without requiring model dependencies.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_GLOB = (
    ROOT
    / "data"
    / "processed"
    / "intervention"
    / "raw"
    / "intervention_*_samples.jsonl"
)
DEFAULT_OUT_DIR = ROOT / "data" / "processed" / "intervention"
TASK_LABELS = {
    "calculator_only": "Calculator (dormant)",
    "planning_search": "Planning (active)",
}


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("cannot take percentile of an empty list")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    weight = pos - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def mean_vectors(rows: list[dict], key: str) -> list[float]:
    vectors = [row[key] for row in rows]
    n = len(vectors)
    width = len(vectors[0])
    return [sum(float(vec[i]) for vec in vectors) / n for i in range(width)]


def empirical_dist(actions: list[int], n_classes: int) -> list[float]:
    counts = [0] * n_classes
    for action in actions:
        counts[int(action)] += 1
    total = float(len(actions))
    return [count / total for count in counts]


def kl_divergence(p: list[float], q: list[float]) -> float:
    total = 0.0
    for pi, qi in zip(p, q):
        if pi > 0.0 and qi > 0.0:
            total += pi * math.log(pi / qi)
    return total


def js_divergence(p: list[float], q: list[float]) -> float:
    midpoint = [(pi + qi) * 0.5 for pi, qi in zip(p, q)]
    return 0.5 * kl_divergence(p, midpoint) + 0.5 * kl_divergence(q, midpoint)


def bootstrap_js(
    wild_rows: list[dict],
    perturbed_rows: list[dict],
    n_classes: int,
    n_bootstrap: int,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    n = len(wild_rows)
    out = []
    for _ in range(n_bootstrap):
        idx = [rng.randrange(n) for _ in range(n)]
        wild_actions = [int(wild_rows[i]["action_index"]) for i in idx]
        pert_actions = [int(perturbed_rows[i]["action_index"]) for i in idx]
        out.append(js_divergence(
            empirical_dist(wild_actions, n_classes),
            empirical_dist(pert_actions, n_classes),
        ))
    return out


def contrast_key_from_row(row: dict) -> str:
    if row.get("contrast_key"):
        return str(row["contrast_key"])
    pert = row["perturbation"]
    return f"{row['task']}/{pert['target']}/{pert['mode']}/{pert['strength']}"


def iter_raw_paths(paths: list[Path] | None) -> list[Path]:
    if paths:
        return sorted(paths)
    return sorted(DEFAULT_RAW_GLOB.parent.glob(DEFAULT_RAW_GLOB.name))


def recompute(raw_paths: Iterable[Path], n_bootstrap: int, seed: int) -> dict[str, dict]:
    wild_by_task: dict[str, dict[str, dict]] = defaultdict(dict)
    perturbed_by_key: dict[str, dict[str, dict]] = defaultdict(dict)
    raw_path_by_key: dict[str, str] = {}

    for raw_path in raw_paths:
        for row in load_jsonl(raw_path):
            task = str(row["task"])
            sample_id = str(row["sample_id"])
            if row["condition"] == "wild":
                wild_by_task[task][sample_id] = row
                continue
            key = contrast_key_from_row(row)
            perturbed_by_key[key][sample_id] = row
            raw_path_by_key[key] = str(raw_path)

    results: dict[str, dict] = {}
    for key, perturbed_by_sample in sorted(perturbed_by_key.items()):
        first = next(iter(perturbed_by_sample.values()))
        task = str(first["task"])
        perturbation = first["perturbation"]
        wild_by_sample = wild_by_task.get(task, {})
        sample_ids = sorted(set(wild_by_sample) & set(perturbed_by_sample))
        if not sample_ids:
            raise ValueError(f"no paired wild samples found for {key}")

        wild_rows = [wild_by_sample[sample_id] for sample_id in sample_ids]
        perturbed_rows = [perturbed_by_sample[sample_id] for sample_id in sample_ids]
        tool_labels = list(first.get("tool_labels") or wild_rows[0]["tool_labels"])
        n_classes = len(tool_labels)

        wild_dist = empirical_dist(
            [int(row["action_index"]) for row in wild_rows],
            n_classes,
        )
        perturbed_dist = empirical_dist(
            [int(row["action_index"]) for row in perturbed_rows],
            n_classes,
        )
        js = js_divergence(wild_dist, perturbed_dist)
        boot = bootstrap_js(wild_rows, perturbed_rows, n_classes, n_bootstrap, seed)
        ci = [percentile(boot, 0.025), percentile(boot, 0.975)]

        wild_mean_probs = mean_vectors(wild_rows, "tool_choice_probs")
        perturbed_mean_probs = mean_vectors(perturbed_rows, "tool_choice_probs")
        soft_js = js_divergence(wild_mean_probs, perturbed_mean_probs)

        results[key] = {
            "task": task,
            "model": first.get("model"),
            "run_seed": first.get("run_seed"),
            "target": perturbation["target"],
            "mode": perturbation["mode"],
            "strength": perturbation["strength"],
            "js_divergence": js,
            "js_ci_95": ci,
            "js_divergence_bits": js / math.log(2),
            "js_ci_95_bits": [ci[0] / math.log(2), ci[1] / math.log(2)],
            "soft_js_divergence": soft_js,
            "soft_js_divergence_bits": soft_js / math.log(2),
            "n_wild": len(wild_rows),
            "n_perturbed": len(perturbed_rows),
            "wild_dist": wild_dist,
            "perturbed_dist": perturbed_dist,
            "wild_mean_tool_choice_probs": wild_mean_probs,
            "perturbed_mean_tool_choice_probs": perturbed_mean_probs,
            "tool_labels": tool_labels,
            "raw_samples_path": raw_path_by_key[key],
            "raw_schema_version": int(first.get("schema_version", 1)),
        }
    return results


def write_outputs(results: dict[str, dict], out_dir: Path, n_bootstrap: int, seed: int) -> None:
    by_task: dict[str, dict[str, dict]] = defaultdict(dict)
    for key, row in results.items():
        by_task[row["task"]][key] = row

    for task, rows in sorted(by_task.items()):
        raw_paths = sorted({row["raw_samples_path"] for row in rows.values()})
        payload = {
            "metadata": {
                "experiment": "react_scratchpad_intervention",
                "processed_level": "raw_recomputed_summary",
                "task": task,
                "model": next(iter(rows.values())).get("model"),
                "n_samples": next(iter(rows.values()))["n_wild"],
                "run_seed": next(iter(rows.values())).get("run_seed"),
                "bootstrap": n_bootstrap,
                "seed": seed,
                "raw_samples_paths": raw_paths,
                "output_schema": "experiments/7.3_intervention/recompute_intervention_summary.py",
                "units": {
                    "js_divergence": "nats",
                    "js_ci_95": "nats",
                    "js_divergence_bits": "bits",
                    "js_ci_95_bits": "bits",
                    "soft_js_divergence": "nats",
                    "soft_js_divergence_bits": "bits",
                },
            },
            **rows,
        }
        write_json(out_dir / f"intervention_{task}.json", payload)

    csv_path = out_dir / "react_intervention_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task",
                "task_label",
                "perturbation",
                "target",
                "mode",
                "strength",
                "js_bits",
                "js_nats",
                "ci_low_bits",
                "ci_high_bits",
                "ci_low_nats",
                "ci_high_nats",
                "soft_js_bits",
                "soft_js_nats",
                "n_wild",
                "n_perturbed",
                "raw_samples_path",
                "raw_schema_version",
            ],
        )
        writer.writeheader()
        for row in sorted(
            results.values(),
            key=lambda r: (r["task"], r["mode"], float(r["strength"])),
        ):
            writer.writerow({
                "task": row["task"],
                "task_label": TASK_LABELS.get(row["task"], row["task"]),
                "perturbation": f"{row['mode']} {float(row['strength']):.1f}",
                "target": row["target"],
                "mode": row["mode"],
                "strength": f"{float(row['strength']):.1f}",
                "js_bits": f"{row['js_divergence_bits']:.4f}",
                "js_nats": f"{row['js_divergence']:.4f}",
                "ci_low_bits": f"{row['js_ci_95_bits'][0]:.4f}",
                "ci_high_bits": f"{row['js_ci_95_bits'][1]:.4f}",
                "ci_low_nats": f"{row['js_ci_95'][0]:.4f}",
                "ci_high_nats": f"{row['js_ci_95'][1]:.4f}",
                "soft_js_bits": f"{row['soft_js_divergence_bits']:.4f}",
                "soft_js_nats": f"{row['soft_js_divergence']:.4f}",
                "n_wild": row["n_wild"],
                "n_perturbed": row["n_perturbed"],
                "raw_samples_path": row["raw_samples_path"],
                "raw_schema_version": row["raw_schema_version"],
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, nargs="*", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    raw_paths = iter_raw_paths(args.raw)
    if not raw_paths:
        raise SystemExit(
            "No raw intervention JSONL files found. Run "
            "`python experiments/7.3_intervention/run_dormant_active.py "
            "--config experiments/7.3_intervention/configs/production.yaml` first."
        )

    results = recompute(raw_paths, args.bootstrap, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_outputs(results, args.out_dir, args.bootstrap, args.seed)
    print(f"wrote {len(results)} contrasts from {len(raw_paths)} raw files to {args.out_dir}")


if __name__ == "__main__":
    main()
