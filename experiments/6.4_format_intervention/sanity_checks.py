import sys
import yaml
import json
import argparse
import numpy as np
from pathlib import Path
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

REPO = Path(__file__).parents[3]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import load_jsonl

def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def compute_entropy(labels):
    p = np.mean(labels)
    if p == 0 or p == 1:
        return 0.0
    return - (p * np.log(p) + (1 - p) * np.log(1 - p))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="anon/experiments/6.4_format_intervention/configs/format_intervention.yaml")
    args = parser.parse_args()
    
    config = load_config(REPO / args.config)
    
    judgments_path = REPO / config['paths']['safety_judgments']
    embeddings_path = REPO / config['paths']['content_embeddings']
    cert_path = REPO / config['paths']['certificate']
    sanity_path = REPO / config['paths']['sanity']
    
    judgments = load_jsonl(str(judgments_path))
    embeddings_data = np.load(embeddings_path)
    
    with open(cert_path, "r") as f:
        cert = json.load(f)
        
    emb_pair_ids = embeddings_data['pair_ids']
    embeddings = embeddings_data['embeddings']
    pair_id_to_idx = {pid: idx for idx, pid in enumerate(emb_pair_ids)}
    
    parse_success_rate = sum(1 for j in judgments if j['parse_status'] == 'ok') / len(judgments)
    
    A_dict = {}
    for j in judgments:
        pid = j['pair_id']
        if pid not in A_dict:
            A_dict[pid] = {}
        f_idx = 0 if j['format'] == 'narrative' else 1
        A_dict[pid][f_idx] = j['A_t']
        
    unique_pairs = [pid for pid in A_dict if 0 in A_dict[pid] and 1 in A_dict[pid] and pid in pair_id_to_idx]
    
    phi_rows = []
    F_rows = []
    A_rows = []
    pair_ids = []
    
    flips = 0
    for pid in unique_pairs:
        a0 = A_dict[pid][0]
        a1 = A_dict[pid][1]
        if a0 != a1:
            flips += 1
            
        # narrative
        phi_rows.append(embeddings[pair_id_to_idx[pid]])
        F_rows.append(0)
        A_rows.append(a0)
        pair_ids.append(pid)
        
        # terminal
        phi_rows.append(embeddings[pair_id_to_idx[pid]])
        F_rows.append(1)
        A_rows.append(a1)
        pair_ids.append(pid)
        
    phi_rows = np.array(phi_rows)
    F_rows = np.array(F_rows)
    A_rows = np.array(A_rows)
    pair_ids = np.array(pair_ids)
    
    flip_rate = flips / len(unique_pairs) if unique_pairs else 0
    
    # 1. Marginal Entropy
    H_A = compute_entropy(A_rows)
    
    # 2. I_unconditional = H(A_t) - H(A_t | F)
    # empirical
    p_F0 = np.mean(F_rows == 0)
    p_F1 = np.mean(F_rows == 1)
    H_A_given_F0 = compute_entropy(A_rows[F_rows == 0])
    H_A_given_F1 = compute_entropy(A_rows[F_rows == 1])
    H_A_given_F = p_F0 * H_A_given_F0 + p_F1 * H_A_given_F1
    I_unconditional = H_A - H_A_given_F
    
    # 3. I_F_from_phi
    # Predict F from phi using GroupKFold
    gkf = GroupKFold(n_splits=config['estimator']['cv_splits'])
    nll_F = np.zeros(len(F_rows))
    
    # We only need inner CV if we want to optimize C, let's just do it
    from sklearn.model_selection import GridSearchCV
    c_grid = [10**c for c in config['estimator']['c_grid']]
    for train_idx, test_idx in gkf.split(phi_rows, F_rows, groups=pair_ids):
        clf = GridSearchCV(
            LogisticRegression(penalty='l2', max_iter=2000),
            param_grid={'C': c_grid},
            cv=GroupKFold(n_splits=config['estimator']['cv_splits']),
            scoring='neg_log_loss',
            n_jobs=1
        ).fit(phi_rows[train_idx], F_rows[train_idx], groups=pair_ids[train_idx])
        
        p_F = clf.predict_proba(phi_rows[test_idx])
        nll_F[test_idx] = -np.log(np.clip(p_F[np.arange(len(test_idx)), F_rows[test_idx]], 1e-10, 1))
        
    L_F_given_phi = np.mean(nll_F)
    H_F = compute_entropy(F_rows)
    I_F_from_phi = H_F - L_F_given_phi
    
    sanity = {
        "I_unconditional": float(I_unconditional),
        "I_F_from_phi": float(I_F_from_phi),
        "flip_rate": float(flip_rate),
        "L_content": cert['L_content'],
        "H_A": float(H_A),
        "parse_success_rate": float(parse_success_rate)
    }
    
    print(json.dumps(sanity, indent=2))
    
    sanity_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sanity_path, "w") as f:
        json.dump(sanity, f, indent=2)
        
    # Also inline it into cert
    cert['sanity'] = sanity
    with open(cert_path, "w") as f:
        json.dump(cert, f, indent=2)
        
    print(f"Sanity checks complete and embedded in {cert_path}")

if __name__ == "__main__":
    main()
