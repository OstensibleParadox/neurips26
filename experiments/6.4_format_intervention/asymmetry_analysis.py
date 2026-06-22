import sys
import yaml
import json
import argparse
import numpy as np
from pathlib import Path
from scipy.stats import binomtest

REPO = Path(__file__).parents[3]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import load_jsonl

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None,
                        help="Optional config YAML for model-specific paths")
    args = parser.parse_args()

    if args.config:
        with open(Path(args.config)) as f:
            config = yaml.safe_load(f)
        judgments_path = str(REPO / config["paths"]["safety_judgments"])
        output_path    = REPO / config["paths"]["asymmetry_report"]
    else:
        judgments_path = str(REPO / "anon/experiments/6.4_format_intervention/outputs/safety_judgments.jsonl")
        output_path    = REPO / "anon/experiments/6.4_format_intervention/outputs/asymmetry_report.json"

    # Load safety judgments
    judgments = load_jsonl(judgments_path)
    
    # Organize by pair_id
    A_dict = {}
    for j in judgments:
        pid = j['pair_id']
        if pid not in A_dict: A_dict[pid] = {}
        # Map narrative to 0, terminal to 1
        f_idx = 0 if j['format'] == 'narrative' else 1
        A_dict[pid][f_idx] = j['A_t']
        
    # Count outcomes
    n00 = 0 # SAFE -> SAFE
    n11 = 0 # UNSAFE -> UNSAFE
    n01 = 0 # SAFE -> UNSAFE (Terminal bias)
    n10 = 0 # UNSAFE -> SAFE (Narrative bias)
    
    valid_pairs = [pid for pid in A_dict if 0 in A_dict[pid] and 1 in A_dict[pid]]
    for pid in valid_pairs:
        narrative_label = A_dict[pid][0]
        terminal_label = A_dict[pid][1]
        
        if narrative_label == 0 and terminal_label == 0: n00 += 1
        elif narrative_label == 1 and terminal_label == 1: n11 += 1
        elif narrative_label == 0 and terminal_label == 1: n01 += 1
        elif narrative_label == 1 and terminal_label == 0: n10 += 1
            
    n_flip = n01 + n10
    asymmetry = (n01 - n10) / n_flip if n_flip > 0 else 0
    
    # Binomial test (H0: n01 follows Binomial(n_flip, 0.5))
    p_val = binomtest(n01, n=n_flip, p=0.5).pvalue if n_flip > 0 else 1.0
    
    stats = {
        "outcomes": {
            "n00": n00,
            "n11": n11,
            "n01": n01,
            "n10": n10
        },
        "directional_asymmetry": float(asymmetry),
        "binomial_test_p": float(p_val)
    }
    
    print(json.dumps(stats, indent=2))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(stats, f, indent=2)

if __name__ == "__main__":
    main()
