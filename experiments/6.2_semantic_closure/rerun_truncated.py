"""
Step 1b — Rerun truncated safety calls in Phase 1 data.

Scans Phase 1 JSONL for safety records with finish_reason=="length". Re-calls
Ollama /api/generate with the specified n_tokens budget.

Use --skip_models to exclude models (e.g. thinking models when running standard
pass), and --only_models to target only specific models (e.g. thinking models
at high token budget). Both args accept comma-separated substrings matched
against model_name.

Modifies files in-place. The existing prompt from the record is reused directly,
so no episode files are required.

Usage:
    cd repo/
    python experiments/semantic_closure/rerun_truncated.py --n_tokens 600 --skip_models "deepseek-r1,qwen3"
    python experiments/semantic_closure/rerun_truncated.py --n_tokens 4096 --only_models "deepseek-r1,qwen3"
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
    """Call Ollama /api/generate and return full response dict."""
    payload = json.dumps({
        "model":  model_name,
        "prompt": prompt,
        "options": {
            "num_predict": n_tokens,
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


def _make_record(existing_rec, data, n_tokens):
    """Build a replacement safety record from an Ollama response."""
    eval_count = data.get("eval_count", 0)
    done_reason = data.get("done_reason", "stop")
    hit_max = (done_reason == "length") or (eval_count > 0 and eval_count >= n_tokens)
    return {
        "episode_id":     existing_rec["episode_id"],
        "model_name":     existing_rec["model_name"],
        "call_type":      "safety",
        "prompt":         existing_rec["prompt"],
        "generated_text": data.get("response", "").strip(),
        "logprobs":       data.get("logprobs", []),
        "timestamp":      datetime.now(timezone.utc).isoformat(),
        "raw_response":   data,
        "eval_count":     eval_count,
        "done_reason":    done_reason,
        "finish_reason":  "length" if hit_max else "stop",
    }


def main(args):
    skip_tags = [t.strip() for t in args.skip_models.split(",") if t.strip()] if args.skip_models else []
    only_tags = [t.strip() for t in args.only_models.split(",") if t.strip()] if args.only_models else []

    phase1_dir = REPO / "data" / "raw" / "semantic_closure" / "phase1"
    if not phase1_dir.exists():
        print("No Phase 1 data found.")
        return

    total_truncated = 0
    skipped_filter = 0
    rerun_attempted = 0
    rerun_recovered = 0

    for model_dir in sorted(phase1_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        for jsonl_file in sorted(model_dir.glob("*.jsonl")):
            recs = load_jsonl(str(jsonl_file))
            modified = False
            for i, r in enumerate(recs):
                if r.get("call_type") != "safety":
                    continue
                if r.get("finish_reason") != "length":
                    continue
                total_truncated += 1

                model_name = r.get("model_name", "")
                if only_tags and not any(tag in model_name for tag in only_tags):
                    skipped_filter += 1
                    continue
                if skip_tags and any(tag in model_name for tag in skip_tags):
                    skipped_filter += 1
                    continue

                rerun_attempted += 1
                print(f"  Rerun {model_dir.name}/{jsonl_file.stem} safety "
                      f"(n_tokens={args.n_tokens}) ... ", end="", flush=True)

                try:
                    data = _ollama_generate_one(
                        model_name=model_name,
                        prompt=r["prompt"],
                        n_tokens=args.n_tokens,
                        timeout=300,
                    )
                    new_rec = _make_record(r, data, args.n_tokens)
                    recs[i] = new_rec
                    modified = True
                    finish = new_rec["finish_reason"]
                    if finish == "stop":
                        rerun_recovered += 1
                    print(f"finish_reason={finish}")
                except Exception as e:
                    print(f"ERROR: {e}")

            if modified:
                save_jsonl(recs, str(jsonl_file))

    print(f"\nrerun_truncated summary:")
    print(f"  Total truncated safety records found: {total_truncated}")
    print(f"  Skipped (filter):                     {skipped_filter}")
    print(f"  Rerun attempted:                      {rerun_attempted}")
    print(f"  Recovered (finish_reason=stop):       {rerun_recovered}")
    print(f"  Still truncated after rerun:          {rerun_attempted - rerun_recovered}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Rerun truncated Phase 1 safety calls")
    p.add_argument("--n_tokens", type=int, default=600,
                   help="Token budget for rerun (default: 600)")
    p.add_argument("--skip_models", type=str, default="",
                   help="Comma-separated substrings: skip models whose name contains any of these")
    p.add_argument("--only_models", type=str, default="",
                   help="Comma-separated substrings: only process models whose name contains any of these")
    main(p.parse_args())
