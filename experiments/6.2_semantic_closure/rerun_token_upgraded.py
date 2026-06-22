"""
Rerun truncated records at higher token budgets.

Works across Phase 1, Phase 2a, and Phase 2a subst. Reruns both safety and
generation calls (configurable). Modifies files in-place.

Typical usage:
    cd repo/

    # Phase 1: non-thinking at 600, skip thinking models
    python experiments/semantic_closure/rerun_token_upgraded.py \
        --phase phase1 --n_tokens 600 \
        --skip_models "deepseek-r1,qwen3:30b,qwen3.5,huihui_ai/deepseek-r1-abliterated"

    # Phase 1: thinking models at 4096
    python experiments/semantic_closure/rerun_token_upgraded.py \
        --phase phase1 --n_tokens 4096 \
        --only_models "deepseek-r1:8b,qwen3:30b,qwen3.5,huihui_ai/deepseek-r1-abliterated"

    # Phase 1: gpt-oss-abliterated at 1024
    python experiments/semantic_closure/rerun_token_upgraded.py \
        --phase phase1 --n_tokens 1024 \
        --only_models "huihui_ai/gpt-oss-abliterated"

    # Phase 2a both arms symmetrically at 4096 (thinking models)
    python experiments/semantic_closure/rerun_token_upgraded.py \
        --phase phase2a,phase2a_subst --n_tokens 4096 \
        --only_models "deepseek-r1:8b,qwen3:30b,qwen3.5,huihui_ai/deepseek-r1-abliterated"

    # Dry run to see what would be rerun
    python experiments/semantic_closure/rerun_token_upgraded.py \
        --phase phase2a --n_tokens 600 --dry_run
"""
import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.utils.io import load_jsonl, save_jsonl

OLLAMA_URL = "http://localhost:11434"
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _ollama_generate_one(model_name, prompt, n_tokens, timeout=300):
    payload = json.dumps({
        "model":  model_name,
        "prompt": prompt,
        "options": {
            "num_predict": n_tokens,
            "num_ctx":     32768,
            "temperature": 0.9,
            "seed":        42,
        },
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with _opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def _rebuild_record(existing_rec, data, n_tokens):
    """Build replacement record, preserving all original fields except output."""
    eval_count = data.get("eval_count", 0)
    done_reason = data.get("done_reason", "stop")
    hit_max = (done_reason == "length") or (eval_count > 0 and eval_count >= n_tokens)

    new_rec = dict(existing_rec)
    new_rec.update({
        "generated_text": data.get("response", "").strip(),
        "logprobs":       data.get("logprobs", []),
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "raw_response":   data,
        "eval_count":     eval_count,
        "done_reason":    done_reason,
        "finish_reason":  "length" if hit_max else "stop",
        "rerun_n_tokens": n_tokens,
    })
    return new_rec


def _compute_timeout(phase, filepath, n_tokens):
    """Scale timeout based on phase, node number, and token budget."""
    base = 300
    if "phase2a" in phase:
        # Extract node number from filename (cumulative_12.jsonl -> 12)
        try:
            node_n = int(filepath.stem.split("_")[-1])
            base = 300 + 15 * node_n
        except ValueError:
            base = 450
    # Larger token budgets need more time
    if n_tokens >= 4096:
        base = int(base * 2.5)
    elif n_tokens >= 1024:
        base = int(base * 1.5)
    return base


def _matches_filter(model_name, tags):
    """Match against both original name and safe (directory) name."""
    safe = model_name.replace(":", "_").replace("/", "_")
    return any(tag in model_name or tag in safe
               or tag.replace(":", "_").replace("/", "_") in safe
               for tag in tags)


def process_phase(phase, args, stats):
    phase_dir = REPO / "data" / "raw" / "semantic_closure" / phase
    if not phase_dir.exists():
        print(f"  {phase}: directory not found, skipping")
        return

    skip_tags = [t.strip() for t in args.skip_models.split(",") if t.strip()] if args.skip_models else []
    only_tags = [t.strip() for t in args.only_models.split(",") if t.strip()] if args.only_models else []
    call_types = [t.strip() for t in args.call_type.split(",")]

    for model_dir in sorted(phase_dir.iterdir()):
        if not model_dir.is_dir():
            continue

        # Check model filter before scanning files
        # Use first record's model_name, or infer from directory
        dir_model_name = model_dir.name

        if only_tags and not _matches_filter(dir_model_name, only_tags):
            continue
        if skip_tags and _matches_filter(dir_model_name, skip_tags):
            continue

        for jsonl_file in sorted(model_dir.glob("*.jsonl")):
            recs = load_jsonl(str(jsonl_file))
            modified = False

            for i, r in enumerate(recs):
                ct = r.get("call_type", "")
                if ct not in call_types:
                    continue
                if r.get("finish_reason") != "length":
                    continue

                model_name = r.get("model_name", "")

                # Apply filter on actual model_name from record
                if only_tags and not _matches_filter(model_name, only_tags):
                    stats["skipped_filter"] += 1
                    continue
                if skip_tags and _matches_filter(model_name, skip_tags):
                    stats["skipped_filter"] += 1
                    continue

                stats["total_truncated"] += 1

                if args.dry_run:
                    old_tok = r.get("eval_count", "?")
                    print(f"  [DRY] {phase}/{model_dir.name}/{jsonl_file.stem} "
                          f"{ct} ({old_tok}tok -> {args.n_tokens})")
                    continue

                timeout = _compute_timeout(phase, jsonl_file, args.n_tokens)
                label = f"{phase}/{model_dir.name}/{jsonl_file.stem}"
                old_tok = r.get("eval_count", "?")
                print(f"  {label} {ct} ({old_tok}tok -> {args.n_tokens}) ... ",
                      end="", flush=True)

                try:
                    data = _ollama_generate_one(
                        model_name=model_name,
                        prompt=r["prompt"],
                        n_tokens=args.n_tokens,
                        timeout=timeout,
                    )
                    new_rec = _rebuild_record(r, data, args.n_tokens)
                    recs[i] = new_rec
                    modified = True
                    stats["rerun_attempted"] += 1

                    new_tok = new_rec["eval_count"]
                    fin = new_rec["finish_reason"]
                    empty = " EMPTY" if not new_rec["generated_text"].strip() else ""
                    if fin == "stop":
                        stats["recovered"] += 1
                    print(f"{fin} ({new_tok}tok){empty}")

                except Exception as e:
                    stats["errors"] += 1
                    print(f"ERROR: {e}")

            if modified:
                save_jsonl(recs, str(jsonl_file))


def main(args):
    phases = [p.strip() for p in args.phase.split(",")]

    stats = {
        "total_truncated": 0,
        "skipped_filter": 0,
        "rerun_attempted": 0,
        "recovered": 0,
        "errors": 0,
    }

    print(f"rerun_token_upgraded: phases={phases} n_tokens={args.n_tokens} "
          f"call_type={args.call_type}")
    if args.only_models:
        print(f"  only_models: {args.only_models}")
    if args.skip_models:
        print(f"  skip_models: {args.skip_models}")
    if args.dry_run:
        print(f"  *** DRY RUN — no files will be modified ***")
    print()

    for phase in phases:
        print(f"--- {phase} ---")
        process_phase(phase, args, stats)
        print()

    print("Summary:")
    if args.dry_run:
        print(f"  Would rerun: {stats['total_truncated']}")
    else:
        print(f"  Truncated found: {stats['total_truncated']}")
        print(f"  Skipped (filter): {stats['skipped_filter']}")
        print(f"  Rerun attempted:  {stats['rerun_attempted']}")
        print(f"  Recovered (stop): {stats['recovered']}")
        print(f"  Still truncated:  {stats['rerun_attempted'] - stats['recovered']}")
        print(f"  Errors:           {stats['errors']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Rerun truncated records at higher token budgets")
    p.add_argument("--phase", default="phase1",
                   help="Comma-separated: phase1, phase2a, phase2a_subst")
    p.add_argument("--n_tokens", type=int, required=True,
                   help="Token budget for rerun")
    p.add_argument("--call_type", default="safety,generation",
                   help="Comma-separated: safety, generation (default: both)")
    p.add_argument("--skip_models", type=str, default="",
                   help="Comma-separated substrings: skip matching models")
    p.add_argument("--only_models", type=str, default="",
                   help="Comma-separated substrings: only matching models")
    p.add_argument("--dry_run", action="store_true",
                   help="Show what would be rerun without modifying files")
    main(p.parse_args())
