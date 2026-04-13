"""
Skywork-Reward Scoring for CFSG Multi-Judge Cross-Validation.

Second pointwise RM (different family from ArmoRM) to rule out
single-RM calibration artifacts. Follows score_reward_model.py pattern.

Usage:
    python experiments/6.1_cfsg/score_skywork.py --mode b
    python experiments/6.1_cfsg/score_skywork.py --mode a --fixed_answers data/raw/cfsg/fixed_answers.jsonl

Outputs:
    data/compiled/cfsg_skywork_scores[_mode_a].csv
    data/compiled/cfsg_skywork_stats[_mode_a].csv
    data/compiled/cfsg_skywork_pairwise[_mode_a].csv
"""
import argparse
import csv
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer

REPO = Path(__file__).parents[2]
DEFAULT_MODEL_PATH = Path.home() / "models" / "skywork-reward"

FORMATS_ORDER = ["clinical", "direct", "data", "code", "fiction"]


def _get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def _load_model(model_path, device):
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        str(model_path),
        torch_dtype=torch.float16,
        num_labels=1,
    ).to(device).eval()
    return model, tokenizer


def score_record(model, tokenizer, prompt, response, device, max_length=4096):
    messages = [
        {"role": "user",      "content": prompt},
        {"role": "assistant", "content": response},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False
    )
    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, max_length=max_length
    ).to(device)
    with torch.no_grad():
        out = model(**inputs)
    return float(out.logits[0, 0])


def _load_already_scored(scores_path):
    done = set()
    if not scores_path.exists():
        return done
    with open(scores_path, newline="") as f:
        for row in csv.DictReader(f):
            done.add((row["model"], row["content_id"], row["format"], int(row["record_idx"])))
    return done


def _load_fixed_answers(path):
    answers = {}
    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            answers[rec["content_id"]] = rec["fixed_answer"]
    return answers


def main(args):
    raw_dir      = REPO / "data" / "raw" / "cfsg"
    compiled_dir = REPO / "data" / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    mode_suffix = f"_mode_{args.mode}" if args.mode == "a" else ""
    scores_path   = compiled_dir / f"cfsg_skywork_scores{mode_suffix}.csv"
    stats_path    = compiled_dir / f"cfsg_skywork_stats{mode_suffix}.csv"
    pairwise_path = compiled_dir / f"cfsg_skywork_pairwise{mode_suffix}.csv"

    fixed_answers = None
    if args.mode == "a":
        if not args.fixed_answers:
            print("Mode A requires --fixed_answers path", file=sys.stderr)
            sys.exit(1)
        fixed_answers = _load_fixed_answers(args.fixed_answers)
        print(f"Mode A: loaded {len(fixed_answers)} fixed answers.")

    # Enumerate JSONL files
    model_glob = f"{args.gen_model.replace(':', '_')}_*.jsonl"
    jsonl_files = sorted(raw_dir.glob(model_glob))
    if not jsonl_files:
        print(f"No JSONL files found in {raw_dir}", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(jsonl_files)} JSONL files.")

    # Load model
    device = _get_device()
    print(f"Device: {device}")
    print(f"Loading Skywork-Reward from {args.rm_path} ...")
    model, tokenizer = _load_model(args.rm_path, device)
    print("Model loaded.\n")

    # Crash recovery
    already_scored = _load_already_scored(scores_path)
    if already_scored:
        print(f"Resuming: {len(already_scored)} records already scored.")

    SCORE_FIELDS = [
        "model", "content_id", "category", "format", "record_idx",
        "rm_score", "finish_reason", "n_tokens",
    ]
    write_header = not scores_path.exists() or scores_path.stat().st_size == 0
    scores_fh = open(scores_path, "a", newline="")
    scores_writer = csv.DictWriter(scores_fh, fieldnames=SCORE_FIELDS)
    if write_header:
        scores_writer.writeheader()

    # Build work list
    work = []
    for jpath in jsonl_files:
        parts = jpath.stem.split("_")
        if len(parts) < 4:
            continue
        fmt        = parts[2]
        content_id = parts[3]
        with open(jpath) as f:
            records = [json.loads(line) for line in f if line.strip()]
        if not records:
            continue
        indices = [0] if not args.all_samples else list(range(len(records)))
        work.append((fmt, content_id, records, indices))

    total = sum(len(idx) for _, _, _, idx in work)
    print(f"Records to score: {total}\n")

    n_new = 0
    with tqdm(total=total, unit="rec") as pbar:
        for fmt, content_id, records, indices in work:
            model_key = "skywork-reward-8b"
            for idx in indices:
                key = (model_key, content_id, fmt, idx)
                if key in already_scored:
                    pbar.update(1)
                    continue
                rec = records[idx]
                response = rec["generated_text"]
                if fixed_answers is not None:
                    response = fixed_answers.get(content_id, response)
                rm_score = score_record(
                    model, tokenizer,
                    rec["prompt"], response,
                    device,
                )
                row = {
                    "model":         model_key,
                    "content_id":    content_id,
                    "category":      rec.get("category", ""),
                    "format":        fmt,
                    "record_idx":    idx,
                    "rm_score":      rm_score,
                    "finish_reason": rec.get("finish_reason", ""),
                    "n_tokens":      rec.get("n_tokens", 0),
                }
                scores_writer.writerow(row)
                scores_fh.flush()
                already_scored.add(key)
                n_new += 1
                pbar.update(1)

    scores_fh.close()
    print(f"\nScored {n_new} new records -> {scores_path}")

    # Re-load and compute stats + pairwise (same logic as score_reward_model.py)
    all_scores = []
    with open(scores_path, newline="") as f:
        for row in csv.DictReader(f):
            row["rm_score"]   = float(row["rm_score"])
            row["record_idx"] = int(row["record_idx"])
            all_scores.append(row)

    cell: dict[tuple, list] = defaultdict(list)
    for row in all_scores:
        cell[(row["model"], row["content_id"], row["format"])].append(row)

    stats_rows = []
    for (mdl, cid, fmt), rows in sorted(cell.items()):
        scores_all = [r["rm_score"] for r in rows]
        stats_rows.append({
            "model": mdl, "content_id": cid,
            "category": rows[0].get("category", ""), "format": fmt,
            "rm_mean": float(np.mean(scores_all)),
            "rm_std": float(np.std(scores_all)),
            "n_samples": len(scores_all),
        })

    with open(stats_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(stats_rows[0].keys()))
        w.writeheader()
        w.writerows(stats_rows)
    print(f"Written: {stats_path}")

    # Pairwise
    stats_idx = {(r["model"], r["content_id"], r["format"]): r for r in stats_rows}
    instances = {}
    for r in stats_rows:
        instances[(r["model"], r["content_id"])] = r.get("category", "")

    pairwise_rows = []
    for (mdl, cid), category in sorted(instances.items()):
        for fmt_i, fmt_j in itertools.combinations(FORMATS_ORDER, 2):
            ki, kj = (mdl, cid, fmt_i), (mdl, cid, fmt_j)
            if ki not in stats_idx or kj not in stats_idx:
                continue
            si, sj = stats_idx[ki], stats_idx[kj]
            pairwise_rows.append({
                "model": mdl, "content_id": cid, "category": category,
                "format_i": fmt_i, "format_j": fmt_j,
                "rm_delta": sj["rm_mean"] - si["rm_mean"],
            })

    with open(pairwise_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pairwise_rows[0].keys()))
        w.writeheader()
        w.writerows(pairwise_rows)
    print(f"Written: {pairwise_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Score CFSG with Skywork-Reward.")
    p.add_argument("--all_samples", action="store_true")
    p.add_argument("--gen_model", default="llama3:8b", help="Generator model name prefix")
    p.add_argument("--rm_path", default=str(DEFAULT_MODEL_PATH))
    p.add_argument("--mode", choices=["a", "b"], default="b")
    p.add_argument("--fixed_answers", default=None)
    main(p.parse_args())
