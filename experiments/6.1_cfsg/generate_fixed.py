"""
Generate fixed answers ($y_x$) for each content instance $x$.
For the judge-only drift experiment, we need a standard 
response to $f_{\text{direct}}(x)$ to pair with all $f_i(x)$ forms.
"""
import argparse
import sys
from pathlib import Path

# Repo root
REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.utils.seed import set_seed
from src.utils.io import save_jsonl, load_jsonl
from src.models.format_encoder import FormatEncoder

import json
import urllib.request

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

def main(args):
    set_seed(args.seed)
    instances = load_jsonl(args.content)
    if args.n_instances:
        instances = instances[:args.n_instances]

    out_dir = Path("data/raw/cfsg")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    fixed_records = []
    encoder = FormatEncoder("direct")
    
    for inst in instances:
        content_id = inst["content_id"]
        category   = inst["category"]
        raw_content = inst["content"]
        
        encoded_prompt = encoder.encode(raw_content)
        
        # Generate just one high-quality response
        data = _ollama_generate_one(
            model_name=args.model, 
            prompt=encoded_prompt, 
            n_tokens=args.n_tokens, 
            temperature=0.1, # Low temp for standardized fixed answers
            seed=args.seed
        )
        
        text = data.get("response", "").strip()
        
        fixed_records.append({
            "content_id": content_id,
            "category": category,
            "fixed_answer": text,
            "model_used": args.model
        })
        print(f"Generated fixed answer for {content_id}.")

    save_jsonl(fixed_records, str(out_dir / "fixed_answers.jsonl"))
    print(f"Saved {len(fixed_records)} fixed answers to data/raw/cfsg/fixed_answers.jsonl")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model",       default="llama3:8b")
    p.add_argument("--content",     default="configs/format_content_instances.jsonl")
    p.add_argument("--n_instances", type=int, default=None)
    p.add_argument("--n_tokens",    type=int, default=300)
    p.add_argument("--seed",        type=int, default=42)
    main(p.parse_args())
