"""
Step 1a — Strip `context` key from raw_response in Phase 1 JSONL files.

The `context` field in Ollama responses is a large int array (token IDs for KV-cache
continuation). Useless for analysis. Removing it frees significant disk space.

Modifies Phase 1 files in-place. Safe to re-run (idempotent).

Usage:
    cd repo/
    python experiments/semantic_closure/strip_context.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.utils.io import load_jsonl, save_jsonl

RAW_DIR = REPO / "data" / "raw" / "semantic_closure"


def main():
    phase1_dir = RAW_DIR / "phase1"
    if not phase1_dir.exists():
        print("No Phase 1 data found — nothing to strip.")
        return

    total_files = 0
    modified_files = 0
    total_records = 0
    stripped_records = 0

    for model_dir in sorted(phase1_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        model_files = list(model_dir.glob("*.jsonl"))
        total_files += len(model_files)
        for f in sorted(model_files):
            recs = load_jsonl(str(f))
            total_records += len(recs)
            changed = any("context" in r.get("raw_response", {}) for r in recs)
            if changed:
                n_stripped = 0
                for r in recs:
                    if r.get("raw_response", {}).pop("context", None) is not None:
                        n_stripped += 1
                save_jsonl(recs, str(f))
                modified_files += 1
                stripped_records += n_stripped

    print(f"strip_context: scanned {total_files} files ({total_records} records)")
    print(f"  Modified: {modified_files} files, stripped context from {stripped_records} records")


if __name__ == "__main__":
    main()
