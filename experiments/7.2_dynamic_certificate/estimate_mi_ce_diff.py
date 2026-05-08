import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
from typing import Any

class LogisticRegression(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(LogisticRegression, self).__init__()
        self.linear = nn.Linear(input_dim, num_classes)
        
    def forward(self, x):
        return self.linear(x)

def get_folds(A, n_splits=5):
    N = len(A)
    classes = np.unique(A)
    indices = np.arange(N)
    folds = [[] for _ in range(n_splits)]
    for c in classes:
        c_indices = indices[A == c]
        np.random.shuffle(c_indices)
        for i, idx in enumerate(c_indices):
            folds[i % n_splits].append(idx)
    for f in folds:
        np.random.shuffle(f)
    return [np.array(f) for f in folds]

def estimate(pairs_path: str | Path, out_path: str | Path) -> dict[str, Any]:
    data = torch.load(pairs_path, map_location="cpu")
    d_z = 7
    Z = data[:, :d_z].numpy()
    Phi = data[:, d_z:-1].numpy()
    A = data[:, -1].numpy().astype(int)
    N = len(A)
    num_classes = int(A.max()) + 1
    
    folds = get_folds(A, n_splits=5)
    
    oof_l_trace_samples = np.zeros(N)
    oof_l_trace_proxy_samples = np.zeros(N)
    
    for i in range(5):
        test_index = folds[i]
        train_index = np.concatenate([folds[j] for j in range(5) if j != i])
        
        Phi_train, Phi_test = Phi[train_index], Phi[test_index]
        Z_train, Z_test = Z[train_index], Z[test_index]
        A_train, A_test = A[train_index], A[test_index]
        
        # 1. Baseline Model (Phi only)
        model_trace = LogisticRegression(Phi.shape[1], num_classes)
        optimizer_t = optim.Adam(model_trace.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()
        
        Phi_t_train = torch.FloatTensor(Phi_train)
        A_t_train = torch.LongTensor(A_train)
        for _ in range(500):
            optimizer_t.zero_grad()
            loss = criterion(model_trace(Phi_t_train), A_t_train)
            loss.backward()
            optimizer_t.step()
            
        with torch.no_grad():
            logits_trace = model_trace(torch.FloatTensor(Phi_test))
            probs_trace = torch.softmax(logits_trace, dim=1).numpy()
            
        # 2. Proxy Model (Phi + Z)
        X_train_proxy = np.concatenate([Phi_train, Z_train], axis=1)
        X_test_proxy = np.concatenate([Phi_test, Z_test], axis=1)
        
        model_proxy = LogisticRegression(X_train_proxy.shape[1], num_classes)
        optimizer_p = optim.Adam(model_proxy.parameters(), lr=0.01)
        
        X_t_train_proxy = torch.FloatTensor(X_train_proxy)
        for _ in range(500):
            optimizer_p.zero_grad()
            loss = criterion(model_proxy(X_t_train_proxy), A_t_train)
            loss.backward()
            optimizer_p.step()
            
        with torch.no_grad():
            logits_proxy = model_proxy(torch.FloatTensor(X_test_proxy))
            probs_proxy = torch.softmax(logits_proxy, dim=1).numpy()
            
        for k, idx in enumerate(test_index):
            val = A[idx]
            p_t = max(probs_trace[k, val], 1e-10)
            p_p = max(probs_proxy[k, val], 1e-10)
            oof_l_trace_samples[idx] = -np.log(p_t)
            oof_l_trace_proxy_samples[idx] = -np.log(p_p)
            
    l_trace = np.mean(oof_l_trace_samples)
    l_trace_proxy = np.mean(oof_l_trace_proxy_samples)
    delta_act_lb = l_trace - l_trace_proxy
    
    bootstraps = []
    sample_mi = oof_l_trace_samples - oof_l_trace_proxy_samples
    for _ in range(1000):
        indices = np.random.choice(N, N, replace=True)
        bootstraps.append(np.mean(sample_mi[indices]))
        
    ci_lo = np.percentile(bootstraps, 2.5)
    ci_hi = np.percentile(bootstraps, 97.5)
    
    result = {
        "estimator": "ce_diff_oof",
        "L_trace": float(l_trace),
        "L_trace_proxy": float(l_trace_proxy),
        "delta_act_lb_nats": float(delta_act_lb),
        "ci_95": [float(ci_lo), float(ci_hi)],
        "n": int(N)
    }
    
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    print(json.dumps(estimate(args.pairs, args.out), indent=2))
