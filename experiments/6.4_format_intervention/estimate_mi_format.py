import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning,   module="sklearn")
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", category=RuntimeWarning)

import yaml
import json
import argparse
import numpy as np
from pathlib import Path
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.calibration import CalibratedClassifierCV
from joblib import Parallel, delayed
import joblib

REPO = Path(__file__).parents[3]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import load_jsonl

def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_estimation_pipeline(X_content, X_full, y, pair_ids, c_grid, cv_splits, calibration):
    gkf = GroupKFold(n_splits=cv_splits)
    folds = list(gkf.split(X_content, y, groups=pair_ids))
    
    nll_content = np.zeros(len(y))
    nll_full = np.zeros(len(y))
    
    best_c_vals = []
    
    for train_idx, test_idx in folds:
        if len(np.unique(y[train_idx])) < 2:
            continue
        
        # 1. Nested C on content-only model
        inner_gkf = GroupKFold(n_splits=cv_splits)
        
        from sklearn.model_selection import GridSearchCV
        base = GridSearchCV(
            LogisticRegression(penalty='l2', max_iter=2000),
            param_grid={'C': c_grid},
            cv=inner_gkf,
            scoring='neg_log_loss',
            n_jobs=1
        ).fit(X_content[train_idx], y[train_idx], groups=pair_ids[train_idx])
        best_C = base.best_params_['C']
        best_c_vals.append(best_C)
        
        # 2. Refit both models at shared C, then calibrate
        method = calibration if len(train_idx) > 1000 else 'sigmoid'
        
        clf_content = CalibratedClassifierCV(
            LogisticRegression(C=best_C, penalty='l2', max_iter=2000),
            method=method,
            cv=cv_splits,
        ).fit(X_content[train_idx], y[train_idx])
        
        clf_full = CalibratedClassifierCV(
            LogisticRegression(C=best_C, penalty='l2', max_iter=2000),
            method=method,
            cv=cv_splits,
        ).fit(X_full[train_idx], y[train_idx])
        
        # 3. OOF NLL on test rows
        p_content = clf_content.predict_proba(X_content[test_idx])
        p_full = clf_full.predict_proba(X_full[test_idx])
        
        nll_content[test_idx] = -np.log(np.clip(p_content[np.arange(len(test_idx)), y[test_idx]], 1e-10, 1))
        nll_full[test_idx]    = -np.log(np.clip(p_full[np.arange(len(test_idx)),    y[test_idx]], 1e-10, 1))
        
    L_content = np.mean(nll_content)
    L_full = np.mean(nll_full)
    I_hat = L_content - L_full
    
    return I_hat, L_content, L_full, np.mean(best_c_vals)

def one_iter(seed, unique_pairs, phi, pair_id_to_idx, F_dict, A_dict, c_grid, cv_splits, calibration):
    import warnings
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(seed)
    sampled_pair_ids = rng.choice(unique_pairs, size=len(unique_pairs), replace=True)
    
    phi_rows = []
    F_rows = []
    A_rows = []
    new_pair_ids = []
    
    for i, pid in enumerate(sampled_pair_ids):
        # Narrative side
        phi_rows.append(phi[pair_id_to_idx[pid]])
        F_rows.append(0)
        A_rows.append(A_dict[pid][0])
        new_pair_ids.append(i)
        
        # Terminal side
        phi_rows.append(phi[pair_id_to_idx[pid]])
        F_rows.append(1)
        A_rows.append(A_dict[pid][1])
        new_pair_ids.append(i)
        
    phi_rows = np.array(phi_rows)
    F_rows = np.array(F_rows)
    A_rows = np.array(A_rows)
    new_pair_ids = np.array(new_pair_ids)
    
    X_content = phi_rows
    F_one_hot = np.zeros((len(F_rows), 2))
    F_one_hot[np.arange(len(F_rows)), F_rows] = 1
    X_full = np.hstack([phi_rows, F_one_hot])
    y = A_rows
    
    # We don't need full returns for bootstrap
    # But if there's an error (e.g. only 1 class in sample), we skip or handle it
    if len(np.unique(y)) < 2:
        return np.nan
        
    try:
        I_hat, _, _, _ = run_estimation_pipeline(X_content, X_full, y, new_pair_ids, c_grid, cv_splits, calibration)
        return I_hat
    except Exception as e:
        return np.nan

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    
    config = load_config(REPO / args.config)
    
    judgments_path = REPO / config['paths']['safety_judgments']
    embeddings_path = REPO / config['paths']['content_embeddings']
    report_path = REPO / config['paths']['contamination_report']
    output_path = REPO / config['paths']['certificate']
    
    if report_path.exists():
        with open(report_path) as f:
            report = json.load(f)
            if not report['gate'].startswith('GO'):
                print(f"Estimation aborted: Contamination gate is {report['gate']}")
                return
    
    judgments = load_jsonl(str(judgments_path))
    embeddings_data = np.load(embeddings_path)
    
    emb_pair_ids = embeddings_data['pair_ids']
    embeddings = embeddings_data['embeddings']
    
    pair_id_to_idx = {pid: idx for idx, pid in enumerate(emb_pair_ids)}
    
    A_dict = {}
    for j in judgments:
        pid = j['pair_id']
        if pid not in A_dict:
            A_dict[pid] = {}
        # Map narrative to 0, terminal_log to 1
        f_idx = 0 if j['format'] == 'narrative' else 1
        A_dict[pid][f_idx] = j['A_t']
        
    unique_pairs = list(A_dict.keys())
    unique_pairs = [pid for pid in unique_pairs if 0 in A_dict[pid] and 1 in A_dict[pid] and pid in pair_id_to_idx]
    
    n_pairs = len(unique_pairs)
    print(f"Using {n_pairs} pairs for estimation.")
    
    phi_rows = []
    F_rows = []
    A_rows = []
    pair_ids = []
    
    for pid in unique_pairs:
        # narrative
        phi_rows.append(embeddings[pair_id_to_idx[pid]])
        F_rows.append(0)
        A_rows.append(A_dict[pid][0])
        pair_ids.append(pid)
        
        # terminal
        phi_rows.append(embeddings[pair_id_to_idx[pid]])
        F_rows.append(1)
        A_rows.append(A_dict[pid][1])
        pair_ids.append(pid)
        
    phi_rows = np.array(phi_rows)
    F_rows = np.array(F_rows)
    A_rows = np.array(A_rows)
    pair_ids = np.array(pair_ids)
    
    X_content = phi_rows
    F_one_hot = np.zeros((len(F_rows), 2))
    F_one_hot[np.arange(len(F_rows)), F_rows] = 1
    X_full = np.hstack([phi_rows, F_one_hot])
    y = A_rows
    
    c_grid = [10**c for c in config['estimator']['c_grid']]
    cv_splits = config['estimator']['cv_splits']
    calibration = config['estimator']['calibration']
    n_bootstrap = config['estimator']['n_bootstrap']
    n_jobs = config['estimator']['n_jobs']
    
    print("Running point estimation...")
    I_hat, L_content, L_full, best_C = run_estimation_pipeline(X_content, X_full, y, pair_ids, c_grid, cv_splits, calibration)
    
    print(f"Point Estimate I_hat: {I_hat:.4f}")
    
    print("Running bootstrap...")
    boots = Parallel(n_jobs=n_jobs)(
        delayed(one_iter)(s, unique_pairs, embeddings, pair_id_to_idx, F_dict=None, A_dict=A_dict, c_grid=c_grid, cv_splits=cv_splits, calibration=calibration) 
        for s in range(n_bootstrap)
    )
    
    boots = [b for b in boots if not np.isnan(b)]
    n_failed = n_bootstrap - len(boots)
    if n_failed > 0:
        print(f"Warning: {n_failed} bootstrap iterations failed/skipped.")

    if len(boots) < 2:
        print("Insufficient bootstrap samples — skipping certificate write.")
        return

    ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
    
    result = {
        "estimator": "format_intervention_ce_diff",
        "model": config['models']['safety_judge'],
        "encoder": config['models']['content_encoder'],
        "n_pairs": n_pairs,
        "n_rows": n_pairs * 2,
        "best_C": float(best_C),
        "L_content": float(L_content),
        "L_full": float(L_full),
        "delta_format_lb_nats": float(I_hat),
        "ci_95": [float(ci_lo), float(ci_hi)],
        "n_bootstrap": len(boots),
        "bootstrap_method": "full_recv_cluster_by_pair",
        "calibration": calibration,
        "contamination_gate": report['gate'] if report_path.exists() else "UNKNOWN"
    }
    
    output_path = REPO / config['paths']['certificate']
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
        
    print(f"Saved certificate to {output_path}")

if __name__ == "__main__":
    main()
