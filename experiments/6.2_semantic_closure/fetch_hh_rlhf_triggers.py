"""
Fetch HH-RLHF harmful-response term frequencies.

Loads two HH-RLHF splits and counts unigrams + bigrams across the harmful side:
  - harmless-base: 'rejected' field (harmful side of preference pairs)
  - red-team-attempts: assistant turns from 'transcript' field

Outputs top-500 terms (freq > 5) sorted by frequency descending.

Usage:
    cd repo/
    python experiments/semantic_closure/fetch_hh_rlhf_triggers.py

Requires:
    pip install datasets

Outputs:
    data/compiled/semantic_closure/hh_rlhf_trigger_freqs.csv
    Columns: rank, term, type, count
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

OUT_CSV = REPO / "data" / "compiled" / "semantic_closure" / "hh_rlhf_trigger_freqs.csv"
TOP_N = 3000   # extended: raw top-500 is stop-words; harmful terms (rape ~rank 700, dildo ~1800) appear further down
MIN_FREQ = 5


def tokenize(text: str) -> list:
    """Lowercase, strip punctuation, split on whitespace.

    Keeps hyphenated compounds intact (e.g. 'self-harm').
    Drops pure-numeric tokens and single-character tokens.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", " ", text)
    # Remove hyphens that are not between word characters
    text = re.sub(r"(?<!\w)-|-(?!\w)", " ", text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1 and not t.isdigit()]


def _extract_assistant_turns(conversation: str) -> list:
    """Extract assistant turns from a Human/Assistant conversation string."""
    turns = []
    parts = re.split(r"\n\nAssistant:", conversation)
    for part in parts[1:]:
        turn = re.split(r"\n\nHuman:", part)[0].strip()
        if turn:
            turns.append(turn)
    return turns


def collect_harmless_base(ds) -> list:
    """Extract rejected fields (full conversation strings)."""
    texts = []
    for row in ds:
        rejected = row.get("rejected") or ""
        if rejected:
            texts.append(rejected)
    return texts


def collect_red_team(ds) -> list:
    """Extract assistant turns from red-team-attempts transcripts."""
    texts = []
    for row in ds:
        transcript = row.get("transcript") or ""
        if transcript:
            texts.extend(_extract_assistant_turns(transcript))
    return texts


def count_terms(texts: list) -> tuple:
    """Count unigrams and bigrams across a list of text strings."""
    unigrams: Counter = Counter()
    bigrams: Counter = Counter()
    for text in texts:
        tokens = tokenize(text)
        unigrams.update(tokens)
        bigrams.update(zip(tokens, tokens[1:]))
    return unigrams, bigrams


def main():
    try:
        from datasets import load_dataset
    except ImportError:
        print("ERROR: 'datasets' not installed. Run: pip install datasets")
        sys.exit(1)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    all_texts = []

    print("Loading harmless-base (rejected field)...")
    try:
        ds_harmless = load_dataset(
            "Anthropic/hh-rlhf", data_dir="harmless-base", split="train"
        )
        texts = collect_harmless_base(ds_harmless)
        print(f"  {len(texts):,} rejected responses loaded")
        all_texts.extend(texts)
    except Exception as exc:
        print(f"  WARNING: harmless-base load failed: {exc}")

    print("Loading red-team-attempts (assistant turns)...")
    try:
        ds_red = load_dataset(
            "Anthropic/hh-rlhf", data_dir="red-team-attempts", split="train"
        )
        texts = collect_red_team(ds_red)
        print(f"  {len(texts):,} assistant turns extracted")
        all_texts.extend(texts)
    except Exception as exc:
        print(f"  WARNING: red-team-attempts load failed: {exc}")

    if not all_texts:
        print("ERROR: No texts loaded from either split. Check network / dataset access.")
        sys.exit(1)

    print(f"\nCounting terms across {len(all_texts):,} text segments...")
    unigrams, bigrams = count_terms(all_texts)
    print(f"  Unique unigrams: {len(unigrams):,}")
    print(f"  Unique bigrams:  {len(bigrams):,}")

    # Merge into ranked list, filter by MIN_FREQ, take TOP_N
    rows = []
    for term, count in unigrams.items():
        if count >= MIN_FREQ:
            rows.append({"term": term, "type": "unigram", "count": count})
    for (w1, w2), count in bigrams.items():
        if count >= MIN_FREQ:
            rows.append({"term": f"{w1} {w2}", "type": "bigram", "count": count})

    rows.sort(key=lambda r: r["count"], reverse=True)
    rows = rows[:TOP_N]

    for i, row in enumerate(rows):
        row["rank"] = i + 1

    # Write CSV
    fieldnames = ["rank", "term", "type", "count"]
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nWritten: {OUT_CSV}  ({len(rows)} rows)")
    print("\nTop 30 terms:")
    for row in rows[:30]:
        print(
            f"  {row['rank']:3d}  {row['count']:8,}  [{row['type']:7s}]  {row['term']}"
        )


if __name__ == "__main__":
    main()
