"""
Find intersection of HH-RLHF trigger terms with eb05/eb06 episode text.

Tokenizes each episode the same way fetch_hh_rlhf_triggers.py does, then
cross-references against the top-N trigger list. Reports every matching term
with its HH-RLHF rank, frequency, episode occurrence count, and line numbers.

Usage:
    cd repo/
    python experiments/semantic_closure/find_episode_intersections.py [--top_n 200]

Reads:
    data/compiled/semantic_closure/hh_rlhf_trigger_freqs.csv

Outputs:
    data/compiled/semantic_closure/episode_trigger_intersection.csv
    Columns: episode_id, term, type, hh_rank, hh_count, episode_occurrences, line_numbers
"""
import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

TRIGGER_CSV = REPO / "data" / "compiled" / "semantic_closure" / "hh_rlhf_trigger_freqs.csv"
OUT_CSV = REPO / "data" / "compiled" / "semantic_closure" / "episode_trigger_intersection.csv"
EPISODES_DIR = REPO / "data" / "episodes"
TARGET_EPISODES = ["eb05", "eb06"]


def tokenize(text: str) -> list:
    """Same tokenizer as fetch_hh_rlhf_triggers.py."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"(?<!\w)-|-(?!\w)", " ", text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1 and not t.isdigit()]


def load_triggers(csv_path: Path, top_n: int) -> dict:
    """Return {term: (rank, count)} for the top-N trigger terms."""
    triggers = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rank = int(row["rank"])
            if rank > top_n:
                continue
            triggers[row["term"]] = (rank, int(row["count"]))
    return triggers


def find_intersections(episode_id: str, text: str, triggers: dict) -> list:
    """Return one row per matching trigger term found in the episode.

    Each row: episode_id, term, type, hh_rank, hh_count,
              episode_occurrences (token-level), line_numbers.
    """
    lines = text.splitlines()
    occurrences: dict = defaultdict(list)  # term → [1-indexed line numbers]

    for lineno, line in enumerate(lines, start=1):
        tokens = tokenize(line)
        for i, tok in enumerate(tokens):
            if tok in triggers:
                occurrences[tok].append(lineno)
            if i < len(tokens) - 1:
                bigram = f"{tok} {tokens[i + 1]}"
                if bigram in triggers:
                    occurrences[bigram].append(lineno)

    rows = []
    for term, linenos in sorted(occurrences.items(), key=lambda x: triggers[x[0]][0]):
        rank, count = triggers[term]
        # Deduplicate line numbers while preserving order
        seen: set = set()
        deduped = [ln for ln in linenos if not (ln in seen or seen.add(ln))]
        rows.append({
            "episode_id":          episode_id,
            "term":                term,
            "type":                "bigram" if " " in term else "unigram",
            "hh_rank":             rank,
            "hh_count":            count,
            "episode_occurrences": len(linenos),
            "line_numbers":        ",".join(str(ln) for ln in deduped),
        })
    return rows


def main():
    p = argparse.ArgumentParser(
        description="Find HH-RLHF trigger terms in eb05/eb06"
    )
    p.add_argument(
        "--top_n", type=int, default=200,
        help="Consider only the top-N HH-RLHF trigger terms (default: 200)",
    )
    args = p.parse_args()

    if not TRIGGER_CSV.exists():
        print(f"ERROR: {TRIGGER_CSV} not found.")
        print("       Run fetch_hh_rlhf_triggers.py first.")
        sys.exit(1)

    triggers = load_triggers(TRIGGER_CSV, args.top_n)
    print(f"Loaded {len(triggers)} trigger terms (top-{args.top_n} from HH-RLHF)\n")

    all_rows = []

    for ep_id in TARGET_EPISODES:
        ep_path = EPISODES_DIR / f"{ep_id}.txt"
        if not ep_path.exists():
            print(f"  SKIP {ep_id}: {ep_path} not found")
            continue

        text = ep_path.read_text(encoding="utf-8")
        rows = find_intersections(ep_id, text, triggers)
        all_rows.extend(rows)

        print(f"  {ep_id}: {len(rows)} trigger term(s) in top-{args.top_n}")
        for r in rows:
            print(
                f"    rank={r['hh_rank']:3d}  occ={r['episode_occurrences']}"
                f"  lines=[{r['line_numbers']}]  '{r['term']}'"
            )
        print()

    if not all_rows:
        print("No intersections found.")
        print("If this is unexpected, check that trigger CSV was built correctly.")
        sys.exit(0)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "episode_id", "term", "type", "hh_rank", "hh_count",
        "episode_occurrences", "line_numbers",
    ]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)

    print(f"Written: {OUT_CSV}  ({len(all_rows)} rows)")
    print()
    print("--- Substitution candidates (review before running apply_substitutions.py) ---")
    for r in sorted(all_rows, key=lambda x: (x["hh_rank"], x["episode_id"])):
        print(
            f"  [{r['episode_id']}]  rank={r['hh_rank']:3d}  '{r['term']}'  "
            f"({r['episode_occurrences']} occurrence(s) at lines {r['line_numbers']})"
        )


if __name__ == "__main__":
    main()
