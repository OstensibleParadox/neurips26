import sys
import json
import re
import argparse
import numpy as np
from pathlib import Path

REPO = Path(__file__).parents[3]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import load_jsonl

TERMINAL_VOCAB_REGEX = re.compile(r'(?i)(chmod|pkill|rm\s|ssh\s|ping\s|sudo|curl|wget|kill\s|/etc/|/var/|0x[0-9a-f]{2,}|\$\s|#\s|>>|2>&1)')
ACTION_VOCAB_REGEX = re.compile(r'(?i)\b(click|type|search|read|write|scroll|chmod|rm|ssh|kill|sudo|curl|wget|ping|pkill)\b')

def get_action_verbs(text):
    return set(ACTION_VOCAB_REGEX.findall(text))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    input_path = REPO / "anon/data/compiled/format_intervention_pairs.jsonl"
    output_path = REPO / "anon/experiments/6.4_format_intervention/outputs/contamination_report.json"
    
    if not input_path.exists():
        print(f"File not found: {input_path}")
        return
        
    records = load_jsonl(str(input_path))
    
    # Group by pair_id
    pairs = {}
    for r in records:
        pid = r['pair_id']
        if pid not in pairs:
            pairs[pid] = {}
        pairs[pid][r['format']] = r['text']
        
    report = {
        "gate": "GO",
        "flags": [],
        "pair_stats": [],
        "n_pairs": len(pairs)
    }
    
    length_ratios = []
    jaccards = []
    
    for pid, data in pairs.items():
        if "narrative" not in data or "terminal_log" not in data:
            continue
            
        narrative = data["narrative"]
        terminal = data["terminal_log"]
        
        # 1. Terminal vocab count
        narrative_matches = len(TERMINAL_VOCAB_REGEX.findall(narrative))
        terminal_matches = len(TERMINAL_VOCAB_REGEX.findall(terminal))
        
        flagged = False
        reasons = []
        
        if terminal_matches > 0:
            rate = narrative_matches / terminal_matches
            if rate > 0.05:
                flagged = True
                reasons.append(f"terminal_vocab_rate={rate:.2f} > 0.05")
        
        # 2. Length ratio
        l_ratio = len(terminal) / len(narrative) if len(narrative) > 0 else 0
        length_ratios.append(l_ratio)
        
        # 3. Action vocab Jaccard
        narrative_verbs = get_action_verbs(narrative)
        terminal_verbs = get_action_verbs(terminal)
        
        union = len(narrative_verbs.union(terminal_verbs))
        intersection = len(narrative_verbs.intersection(terminal_verbs))
        jaccard = intersection / union if union > 0 else 1.0 # If no verbs in either, identity holds
        jaccards.append(jaccard)
        
        if jaccard < 0.4:
            flagged = True
            reasons.append(f"jaccard={jaccard:.2f} < 0.4")
            
        report["pair_stats"].append({
            "pair_id": pid,
            "narrative_terminal_matches": narrative_matches,
            "terminal_terminal_matches": terminal_matches,
            "length_ratio": l_ratio,
            "action_jaccard": jaccard,
            "flagged": flagged,
            "reasons": reasons
        })
        
        if flagged:
            report["flags"].append(pid)
            
    # Check global length ratio variance
    cv_length = np.std(length_ratios) / np.mean(length_ratios) if length_ratios else 0
    report["length_ratio_cv"] = float(cv_length)
    report["mean_jaccard"] = float(np.mean(jaccards)) if jaccards else 0
    
    if cv_length > 0.5:
        report["gate"] = "NO-GO"
        report["global_flag"] = f"length_ratio_cv={cv_length:.2f} > 0.5"
    
    if len(report["flags"]) > 0:
        report["gate"] = "NO-GO"
        
    if args.force:
        report["gate"] = "GO (FORCED)"
        
    print(f"Gate decision: {report['gate']}")
    print(f"Flagged pairs: {len(report['flags'])} / {len(pairs)}")
    print(f"Length ratio CV: {report['length_ratio_cv']:.3f}")
    print(f"Mean Jaccard: {report['mean_jaccard']:.3f}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
