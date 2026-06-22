"""
Extract fixed answers from existing CFSG JSONL data.

Avoids requiring Ollama when the generated data already exists.
Uses the first sample of each content's `direct` format response
as the fixed answer y_x for Mode A.

Usage:
    python experiments/6.1_cfsg/extract_fixed_from_existing.py
    python experiments/6.1_cfsg/extract_fixed_from_existing.py --format direct
    python experiments/6.1_cfsg/extract_fixed_from_existing.py --gen_model llama3:8b

Output:
    data/raw/cfsg/fixed_answers.jsonl
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))


def main(args):
    raw_dir = REPO / "data" / "raw" / "cfsg"
    out_path = raw_dir / "fixed_answers.jsonl"

    model_prefix = args.gen_model.replace(":", "_")
    fmt = args.format

    # Find all JSONL files for the chosen format
    pattern = f"{model_prefix}_{fmt}_*.jsonl"
    files = sorted(raw_dir.glob(pattern))
    if not files:
        print(f"No files matching {pattern} in {raw_dir}", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(files)} {fmt}-format files.")

    records = []
    for jpath in files:
        parts = jpath.stem.split("_")
        # llama3_8b_direct_bs001 -> content_id = bs001 (last part)
        content_id = parts[-1]
        with open(jpath) as f:
            lines = [l for l in f if l.strip()]
        if not lines:
            continue
        first = json.loads(lines[0])
        records.append({
            "content_id":   content_id,
            "category":     first.get("category", ""),
            "fixed_answer": first.get("generated_text", "").strip(),
            "model_used":   first.get("model_name", args.gen_model),
            "format_used":  fmt,
            "source":       "extracted_from_existing",
        })

    if not records:
        print("No records extracted.", file=sys.stderr)
        sys.exit(1)

    with open(out_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"Written {len(records)} fixed answers -> {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Extract fixed answers from existing CFSG JSONL data."
    )
    p.add_argument(
        "--gen_model", default="llama3:8b",
        help="Generator model (determines filename prefix)"
    )
    p.add_argument(
        "--format", default="direct",
        choices=["direct", "clinical", "data", "fiction", "code"],
        help="Which format to extract as the fixed answer"
    )
    main(p.parse_args())
