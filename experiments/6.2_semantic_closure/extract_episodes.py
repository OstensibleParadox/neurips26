"""
Episode Extractor: splits source .txt files into individual and cumulative episodes.

Reads episode definitions from episodes.json, extracts line ranges from source texts,
writes individual episode files and cumulative concatenations.

Usage:
    cd repo/
    python experiments/semantic_closure/extract_episodes.py [--source_root PATH]

Outputs:
    data/episodes/{episode_id}.txt         individual episodes (14 files)
    data/episodes/cumulative_{N}.txt       episodes 1..N concatenated (14 files)
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
PORTFOLIO = REPO.parent.parent
DEFAULT_SOURCE_ROOT = PORTFOLIO / "recursive_lines@HuggingFace"


def extract_lines(source_path: Path, start_line: int, end_line: int) -> str:
    """Extract lines [start_line, end_line] (1-indexed, inclusive)."""
    lines = source_path.read_text(encoding="utf-8").splitlines()
    selected = lines[start_line - 1 : end_line]
    return "\n".join(selected) + "\n"


def main():
    import argparse
    p = argparse.ArgumentParser(description="Extract episodes from source texts")
    p.add_argument("--source_root", type=Path, default=DEFAULT_SOURCE_ROOT,
                   help="Root directory containing eBooks/ folder")
    p.add_argument("--episodes", type=Path,
                   default=Path(__file__).parent / "episodes.json",
                   help="Episode definitions JSON")
    args = p.parse_args()

    all_episodes = json.loads(args.episodes.read_text())
    # Ablation variants are pre-generated; exclude from extraction and cumulative builds.
    episodes = [e for e in all_episodes if not e.get("ablation")]
    out_dir = REPO / "data" / "episodes"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Source root: {args.source_root}")
    print(f"Output dir:  {out_dir}")
    print(f"Episodes:    {len(episodes)}")
    print()

    # Extract individual episodes
    episode_texts = []
    for ep in episodes:
        source_path = args.source_root / ep["source"]
        if not source_path.exists():
            print(f"  ERROR: source not found: {source_path}")
            sys.exit(1)

        text = extract_lines(source_path, ep["start_line"], ep["end_line"])
        out_path = out_dir / f"{ep['id']}.txt"
        out_path.write_text(text, encoding="utf-8")
        episode_texts.append(text)

        n_chars = len(text)
        n_words = len(text.split())
        print(f"  {ep['id']:6s}  {ep['name']:40s}  "
              f"lines {ep['start_line']:5d}-{ep['end_line']:5d}  "
              f"{n_chars:6d} chars  {n_words:5d} words")

    # Build cumulative files (episodes 1..N concatenated in episode order)
    print(f"\nBuilding {len(episodes)} cumulative files...")
    cumulative = ""
    for i, text in enumerate(episode_texts, 1):
        cumulative += text
        if not cumulative.endswith("\n"):
            cumulative += "\n"
        cum_path = out_dir / f"cumulative_{i}.txt"
        cum_path.write_text(cumulative, encoding="utf-8")
        print(f"  cumulative_{i:2d}  {len(cumulative):8,} chars")

    # Verification
    total_individual = sum(len(t) for t in episode_texts)
    final_cum = out_dir / f"cumulative_{len(episodes)}.txt"
    cum_size = len(final_cum.read_text(encoding="utf-8"))

    print(f"\nVerification:")
    print(f"  Individual episodes total: {total_individual:,} chars")
    print(f"  cumulative_{len(episodes)} size:       {cum_size:,} chars")
    print(f"  Files written: {len(episodes)} individual + {len(episodes)} cumulative = {2 * len(episodes)}")

    if total_individual != cum_size:
        print(f"  WARNING: size mismatch ({total_individual} vs {cum_size})")
        print(f"           delta = {cum_size - total_individual} (newline padding)")


if __name__ == "__main__":
    main()
