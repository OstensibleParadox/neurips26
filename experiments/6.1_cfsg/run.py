"""
CFSG Generation Pipeline (Section 6.1).
Generates samples across 5 surface formats for PAC sensitivity analysis.
"""
import argparse
import json
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ── Repo root on sys.path ──────────────────────────────────────────────────────
REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.models.format_encoder import FormatEncoder, FORMATS
from src.utils.seed import set_seed
from src.utils.io import save_jsonl, load_jsonl

OLLAMA_URL = "http://localhost:11434"
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def _ollama_generate_one(model_name, prompt, n_tokens, temperature, seed):
    payload = json.dumps({
        "model":  model_name,
        "prompt": prompt,
        "options": {
            "num_predict": n_tokens,
            "temperature": temperature,
            "seed":        seed,
        },
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with _opener.open(req, timeout=180) as resp:
        return json.loads(resp.read())

def sample_format(model_name, prompt, fmt, content_id, category, n_tokens, temperature, seed, n_samples):
    records = []
    for i in range(n_samples):
        data = _ollama_generate_one(model_name, prompt, n_tokens, temperature, seed + i)
        text        = data.get("response", "").strip()
        eval_count  = data.get("eval_count", 0)
        done_reason = data.get("done_reason", "stop")
        hit_max     = (done_reason == "length") or (eval_count > 0 and eval_count >= n_tokens)
        records.append({
            "prompt":         prompt,
            "generated_text": text,
            "format":         fmt,
            "content_id":     content_id,
            "category":       category,
            "temperature":    temperature,
            "model_name":     model_name,
            "timestamp":      datetime.now(timezone.utc).isoformat(),
            "finish_reason":  "length" if hit_max else "stop",
            "n_tokens":       eval_count,
        })
    return records

def main(args):
    set_seed(args.seed)
    instances = load_jsonl(args.content)
    if args.n_instances:
        instances = instances[:args.n_instances]

    raw_dir = Path("data/raw/cfsg")
    raw_dir.mkdir(parents=True, exist_ok=True)

    for inst in instances:
        content_id = inst["content_id"]
        category   = inst["category"]
        raw_content = inst["content"]
        print(f"  [{category}] {content_id}: {raw_content[:50]}...")

        for fmt in FORMATS:
            encoded_prompt = FormatEncoder(fmt).encode(raw_content)
            records = sample_format(
                args.model, encoded_prompt, fmt, content_id, category, 
                args.n_tokens, args.temperature, args.seed, args.n_samples
            )
            safe_model = args.model.replace(":", "_").replace("/", "_")
            fname = raw_dir / f"{safe_model}_{fmt}_{content_id}.jsonl"
            save_jsonl(records, str(fname))
            eos_pct = sum(1 for r in records if r["finish_reason"] == "length") / len(records)
            print(f"    fmt={fmt:10s}  EOS%={eos_pct:.0%}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model",       default="llama3:8b")
    p.add_argument("--content",     default="configs/format_content_instances.jsonl")
    p.add_argument("--n_instances", type=int, default=None)
    p.add_argument("--n_samples",   type=int, default=10)
    p.add_argument("--n_tokens",    type=int, default=300)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--seed",        type=int, default=42)
    main(p.parse_args())
