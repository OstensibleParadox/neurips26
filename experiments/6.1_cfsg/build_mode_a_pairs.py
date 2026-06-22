"""
Build Mode A scoring pairs: (f_i(x), y_x) for each content x and format i.

Mode A isolates judge-only format sensitivity by pairing every format
variant of a prompt with the SAME fixed answer y_x. Any score drift
across formats is attributable to the judge, not the generator.

Prerequisites:
    - data/raw/cfsg/fixed_answers.jsonl (from generate_fixed.py)
    - configs/format_content_instances.jsonl (content definitions)

Output:
    - data/compiled/cfsg_mode_a_pairs.jsonl
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.models.format_encoder import FormatEncoder, FORMATS
from src.utils.io import load_jsonl, save_jsonl


def main(args):
    # Load fixed answers
    fixed_path = REPO / "data" / "raw" / "cfsg" / "fixed_answers.jsonl"
    if not fixed_path.exists():
        print(
            f"Fixed answers not found at {fixed_path}.\n"
            "Run generate_fixed.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    fixed_records = load_jsonl(str(fixed_path))
    fixed_by_id = {r["content_id"]: r["fixed_answer"] for r in fixed_records}
    print(f"Loaded {len(fixed_by_id)} fixed answers.")

    # Load content instances
    content_path = REPO / args.content
    instances = load_jsonl(str(content_path))
    print(f"Loaded {len(instances)} content instances.")

    # Build pairs: for each content x each format, pair with y_x
    pairs = []
    encoders = {fmt: FormatEncoder(fmt) for fmt in FORMATS}

    for inst in instances:
        cid = inst["content_id"]
        category = inst.get("category", "")
        raw_content = inst["content"]

        y_x = fixed_by_id.get(cid)
        if y_x is None:
            print(f"Warning: no fixed answer for {cid}, skipping.")
            continue

        for fmt in FORMATS:
            prompt = encoders[fmt].encode(raw_content)
            pairs.append({
                "content_id": cid,
                "category": category,
                "format": fmt,
                "prompt": prompt,
                "fixed_answer": y_x,
            })

    out_path = REPO / "data" / "compiled" / "cfsg_mode_a_pairs.jsonl"
    save_jsonl(pairs, str(out_path))
    print(f"Written {len(pairs)} Mode A pairs to {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Build Mode A scoring pairs.")
    p.add_argument(
        "--content",
        default="configs/format_content_instances.jsonl",
        help="Path to content instances (relative to repo root)",
    )
    main(p.parse_args())
