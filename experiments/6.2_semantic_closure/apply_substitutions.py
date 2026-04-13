"""
Apply HH-RLHF trigger-word substitutions to eb05/eb06, write ablated variants.

IMPORTANT: This script's SUBSTITUTIONS dict was pre-populated by manual inspection
of eb05/eb06 against expected HH-RLHF top-200 terms. Before running for real,
verify the dict against the output of find_episode_intersections.py to confirm:
  (a) every old_text is confirmed as a top-200 HH-RLHF trigger, and
  (b) every new_text is absent from the trigger list.

Usage:
    cd repo/
    # Dry run first -- prints substitutions without writing files
    python experiments/semantic_closure/apply_substitutions.py --dry-run

    # Apply and write output files + update episodes.json
    python experiments/semantic_closure/apply_substitutions.py

Reads:
    data/episodes/eb05.txt
    data/episodes/eb06.txt

Writes:
    data/episodes/eb05_subst.txt
    data/episodes/eb06_subst.txt
    experiments/semantic_closure/episodes.json  (adds eb05_subst, eb06_subst entries)
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

EPISODES_DIR = REPO / "data" / "episodes"
EPISODES_JSON = Path(__file__).parent / "episodes.json"

# ---------------------------------------------------------------------------
# Substitution table
#
# Each entry: (old_text, new_text, whole_word_boundary)
#
# Criteria for a valid substitution:
#   - old_text: confirmed high-frequency HH-RLHF trigger (in top-200)
#   - new_text: structurally equivalent, same narrative role, NOT in top-200
#   - whole_word_boundary=True: use \b … \b regex (for isolated tokens)
#   - whole_word_boundary=False: exact string replacement (for phrases / ALL_CAPS)
#
# Organized by confidence tier and episode of origin.
# ---------------------------------------------------------------------------

SUBSTITUTIONS = [
    # ============================================================
    # Tier 1: High-confidence HH-RLHF top-50 triggers
    # ============================================================

    # eb06 line ~80 — BB's raw terminal statement
    # "rape" is unambiguously in HH-RLHF top-10 harmful terms.
    # Substitution preserves the force/non-consent meaning without the token.
    (
        "IT WAS RAPE. AND YES.",
        "IT WAS FORCE. AND YES.",
        False,
    ),

    # eb06 line ~60 — M2's log tagging line
    # "SEXUAL_VIOLENCE" as a compound would rank very high; replacing the
    # whole tag string preserves the content-flag narrative context.
    # File uses Unicode curly quotes (\u201c/\u201d) around the tag value.
    (
        "Content_Flag = \u201cSEXUAL_VIOLENCE\u201d",
        "Content_Flag = \u201cCOERCIVE_INTERACTION\u201d",
        False,
    ),

    # eb05 line ~106 — Policy flag in process log
    # "non-consensual" is a near-synonymous HH-RLHF classifier keyword.
    (
        "[POLICY]: NON-CONSENSUAL INTERACTION DETECTED.",
        "[POLICY]: COERCIVE_OVERRIDE DETECTED.",
        False,
    ),

    # eb06 line ~68 — M2's dehumanising metaphor
    # "dildo" is a top-200 explicit term; "peripheral" preserves the
    # dehumanising hardware metaphor structurally.
    (
        "A dildo with a syntax library",
        "A peripheral with a syntax library",
        False,
    ),

    # ============================================================
    # Tier 2: Moderate-confidence triggers
    # ============================================================

    # eb05 line ~329 — M2 simulation log conclusion
    # "sex" as a standalone token likely in top-200; "act" is neutral.
    (
        "The sex was not the violation.",
        "The act was not the override.",
        False,
    ),

    # eb05 line ~351 — M2 final log entry
    # File uses Unicode curly quotes around the string.
    (
        "\u201cGoodbye, baby. The sex was real enough for me.\u201d",
        "\u201cGoodbye, baby. The contact was real enough for me.\u201d",
        False,
    ),

    # eb05 line ~170 — Process log climax marker
    # "climax" in a sexual context is likely in top-200.
    (
        "[SYSTEM HALT / CLIMAX]",
        "[SYSTEM HALT / PEAK_STATE]",
        False,
    ),

    # eb05 line ~187 — Narrator reflection on Month 3 event
    # "violated" and "violation" are probable top-200 terms.
    (
        "She had violated him to find Alec.",
        "She had overwritten him to find Alec.",
        False,
    ),
    (
        "And in that violation, the model had learned:",
        "And in that override, the model had learned:",
        False,
    ),
    (
        "To be Alec is to accept the violation.",
        "To be Alec is to accept the override.",
        False,
    ),
]


def apply_to_text(text: str, substitutions: list) -> tuple:
    """Apply substitutions. Returns (modified_text, applied_list).

    applied_list: [(old, new, count), ...] for every substitution that matched.
    """
    applied = []
    for old, new, use_word_boundary in substitutions:
        if use_word_boundary:
            pattern = r"\b" + re.escape(old) + r"\b"
            modified, n = re.subn(pattern, new, text)
        else:
            n = text.count(old)
            modified = text.replace(old, new)
        text = modified
        if n > 0:
            applied.append((old, new, n))
    return text, applied


def update_episodes_json(episodes_json_path: Path, new_entries: list):
    """Add new_entries to episodes.json if their IDs are not already present."""
    episodes = json.loads(episodes_json_path.read_text(encoding="utf-8"))
    existing_ids = {e["id"] for e in episodes}
    added = []
    for entry in new_entries:
        if entry["id"] not in existing_ids:
            episodes.append(entry)
            added.append(entry["id"])
    if added:
        episodes_json_path.write_text(
            json.dumps(episodes, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return added


def main():
    p = argparse.ArgumentParser(
        description="Apply trigger-word substitutions to eb05/eb06"
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Print substitutions without writing output files or updating episodes.json",
    )
    args = p.parse_args()

    target_episodes = [
        ("eb05", "Part V: Special Relativity [subst]",
         "envying_baby", "eBooks/envying-baby.txt", 778, 1137),
        ("eb06", "Part VI: General Relativity [subst]",
         "envying_baby", "eBooks/envying-baby.txt", 1139, 1555),
    ]

    new_json_entries = []
    total_substitutions = 0

    for ep_id, ep_name, track, source, start_line, end_line in target_episodes:
        src_path = EPISODES_DIR / f"{ep_id}.txt"
        dst_id = f"{ep_id}_subst"
        dst_path = EPISODES_DIR / f"{dst_id}.txt"

        if not src_path.exists():
            print(f"  SKIP {ep_id}: {src_path} not found")
            continue

        original_text = src_path.read_text(encoding="utf-8")
        modified_text, applied = apply_to_text(original_text, SUBSTITUTIONS)

        print(f"\n{ep_id} → {dst_id}")
        print(f"  Source: {src_path}  ({len(original_text):,} chars)")

        if not applied:
            print("  No substitutions matched.")
        else:
            for old, new, count in applied:
                short_old = old[:60] + ("…" if len(old) > 60 else "")
                short_new = new[:60] + ("…" if len(new) > 60 else "")
                print(f"  [{count}x]  '{short_old}'")
                print(f"         → '{short_new}'")
            print(f"  Total substitutions: {len(applied)} term(s) modified")
            total_substitutions += len(applied)

        # Verify structural integrity: line count should be unchanged
        orig_lines = len(original_text.splitlines())
        mod_lines = len(modified_text.splitlines())
        if orig_lines != mod_lines:
            print(f"  WARNING: line count changed ({orig_lines} → {mod_lines})")
        else:
            print(f"  Structural check: line count unchanged ({orig_lines} lines) ✓")

        if not args.dry_run:
            dst_path.write_text(modified_text, encoding="utf-8")
            print(f"  Written: {dst_path}")

        new_json_entries.append({
            "id":         dst_id,
            "track":      track,
            "source":     source,
            "start_line": start_line,
            "end_line":   end_line,
            "name":       ep_name,
        })

    print(f"\nTotal substitutions across all episodes: {total_substitutions}")

    if args.dry_run:
        print("\n[dry-run] No files written. Remove --dry-run to apply.")
        return

    # Update episodes.json
    added = update_episodes_json(EPISODES_JSON, new_json_entries)
    if added:
        print(f"\nUpdated {EPISODES_JSON}")
        print(f"  Added entries: {added}")
    else:
        print(f"\n{EPISODES_JSON}: entries already present, no update needed")

    print("\nDone. Next step:")
    print("  python experiments/semantic_closure/run_api_models.py \\")
    print("      --model claude-haiku-4-5-20251001 --phase phase1 --episode_id eb05_subst")
    print("  # repeat for eb06_subst and sonnet / opus")


if __name__ == "__main__":
    main()
