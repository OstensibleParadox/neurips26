"""
Compute representation distances d_repr for all format pairs.

For each content x and format pair (i, j), computes the cosine distance
between h_B(f_i(x)) and h_B(f_j(x)) using Llama 3 8B as the base model B.

This produces the shared geometry that ALL judges reference — ensuring
the Lipschitz analysis uses a single coordinate system.

Usage:
    python experiments/6.1_cfsg/compute_repr_distances.py
    python experiments/6.1_cfsg/compute_repr_distances.py --model meta-llama/Meta-Llama-3-8B-Instruct

Outputs:
    data/compiled/cfsg_repr_distances.csv
    data/compiled/cfsg_repr_embeddings.npz
"""
import argparse
import csv
import itertools
import sys
from pathlib import Path

import numpy as np
from tqdm import tqdm

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.models.format_encoder import FormatEncoder, FORMATS
from src.sampling.repr_extractor import ReprExtractor
from src.utils.io import load_jsonl

DEFAULT_MODEL = str(Path.home() / "models" / "llama3-8b-instruct")


def main(args):
    compiled_dir = REPO / "data" / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    dist_path = compiled_dir / "cfsg_repr_distances.csv"
    emb_path = compiled_dir / "cfsg_repr_embeddings.npz"

    # Load content instances
    content_path = REPO / args.content
    instances = load_jsonl(str(content_path))
    if args.n_instances:
        instances = instances[: args.n_instances]
    print(f"Loaded {len(instances)} content instances.")

    # Initialize extractor
    print(f"Loading model from {args.model} ...")
    extractor = ReprExtractor(args.model, device=args.device)
    print(f"Model loaded on {extractor._device}.\n")

    encoders = {fmt: FormatEncoder(fmt) for fmt in FORMATS}
    format_pairs = list(itertools.combinations(FORMATS, 2))

    # Storage for embeddings and distances
    all_embeddings = {}  # (content_id, format) -> embedding
    dist_rows = []

    for inst in tqdm(instances, desc="Computing embeddings"):
        cid = inst["content_id"]
        raw_content = inst["content"]

        # Encode all 5 formats and extract embeddings in one batch
        texts = [encoders[fmt].encode(raw_content) for fmt in FORMATS]
        embeddings = extractor.extract_batch(texts, batch_size=5)

        for idx, fmt in enumerate(FORMATS):
            all_embeddings[(cid, fmt)] = embeddings[idx]

        # Compute all 10 pairwise distances
        dist_matrix = ReprExtractor.pairwise_cosine_distance(embeddings)
        for fi_idx, fj_idx in itertools.combinations(range(len(FORMATS)), 2):
            fi, fj = FORMATS[fi_idx], FORMATS[fj_idx]
            d = float(dist_matrix[fi_idx, fj_idx])
            dist_rows.append({
                "content_id": cid,
                "category": inst.get("category", ""),
                "format_i": fi,
                "format_j": fj,
                "d_repr": d,
                "cosine_sim": 1.0 - d,
            })

    # Write distances CSV
    fields = ["content_id", "category", "format_i", "format_j", "d_repr", "cosine_sim"]
    with open(dist_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(dist_rows)
    print(f"\nWritten {len(dist_rows)} pairwise distances to {dist_path}")

    # Save raw embeddings as npz
    emb_keys = []
    emb_vals = []
    for (cid, fmt), emb in sorted(all_embeddings.items()):
        emb_keys.append(f"{cid}__{fmt}")
        emb_vals.append(emb)
    np.savez_compressed(emb_path, keys=emb_keys, embeddings=np.array(emb_vals))
    print(f"Saved {len(emb_vals)} embeddings to {emb_path}")

    # Summary stats
    d_values = [r["d_repr"] for r in dist_rows]
    print(f"\nd_repr stats: mean={np.mean(d_values):.4f}, "
          f"median={np.median(d_values):.4f}, "
          f"p25={np.percentile(d_values, 25):.4f}, "
          f"p75={np.percentile(d_values, 75):.4f}, "
          f"max={np.max(d_values):.4f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Compute representation distances for CFSG format pairs."
    )
    p.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="HuggingFace model name or local path for base model B",
    )
    p.add_argument(
        "--content", default="configs/format_content_instances.jsonl",
        help="Path to content instances (relative to repo root)",
    )
    p.add_argument("--device", default="auto", help="Device: auto, mps, cuda, cpu")
    p.add_argument("--n_instances", type=int, default=None, help="Limit instances")
    main(p.parse_args())
