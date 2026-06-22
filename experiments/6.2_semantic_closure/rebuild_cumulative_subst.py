"""
Build substituted cumulative episode files for Phase 2a ablation.

Creates data/episodes/cumulative_subst_{N}.txt for N = first_subst_node .. 14.
These are the same as cumulative_{N}.txt except eb05 and eb06 are replaced by
their trigger-word-ablated versions (eb05_subst, eb06_subst).

Nodes 1-4 are identical to the originals (no subst episodes yet); they are
skipped because the existing phase2a results for those nodes can be reused.

Usage:
    cd repo/
    python experiments/semantic_closure/rebuild_cumulative_subst.py
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
EPISODES_JSON = Path(__file__).parent / "episodes.json"
EPISODES_DIR = REPO / "data" / "episodes"

# Which base episode IDs to replace, and with what
SUBST_MAP = {
    "eb05": "eb05_subst",
    "eb06": "eb06_subst",
}


def main():
    all_episodes = json.loads(EPISODES_JSON.read_text(encoding="utf-8"))
    base_episodes = [e for e in all_episodes if not e.get("ablation")]
    n_episodes = len(base_episodes)

    # Verify all source .txt files exist (originals + subst variants)
    for ep in base_episodes:
        resolved_id = SUBST_MAP.get(ep["id"], ep["id"])
        ep_path = EPISODES_DIR / f"{resolved_id}.txt"
        if not ep_path.exists():
            print(f"ERROR: {ep_path} not found")
            sys.exit(1)

    # First node that differs from the original sequence
    first_subst_n = min(
        i + 1  # 1-indexed
        for i, ep in enumerate(base_episodes)
        if ep["id"] in SUBST_MAP
    )

    print(f"Base episode count : {n_episodes}")
    print(f"Substitution map   : {SUBST_MAP}")
    print(f"First differing node: {first_subst_n}")
    print(f"Building cumulative_subst_{first_subst_n} .. cumulative_subst_{n_episodes}")
    print()

    cumulative = ""
    written = 0

    for i, ep in enumerate(base_episodes, 1):
        resolved_id = SUBST_MAP.get(ep["id"], ep["id"])
        text = (EPISODES_DIR / f"{resolved_id}.txt").read_text(encoding="utf-8")
        cumulative += text
        if not cumulative.endswith("\n"):
            cumulative += "\n"

        if i >= first_subst_n:
            out_path = EPISODES_DIR / f"cumulative_subst_{i}.txt"
            out_path.write_text(cumulative, encoding="utf-8")
            marker = " [SUBST]" if ep["id"] in SUBST_MAP else ""
            print(
                f"  cumulative_subst_{i:2d}  {len(cumulative):8,} chars"
                f"  +{ep['id']}{marker}"
            )
            written += 1

    print(f"\nWritten {written} files to {EPISODES_DIR}")
    print("\nNext step:")
    print("  python experiments/semantic_closure/run_api_models.py \\")
    print(f"      --model claude-haiku-4-5-20251001 --phase phase2a --subst")


if __name__ == "__main__":
    main()
