"""
Metrics for Screenability and PAC analysis.
Renamed and simplified from legacy agency_index library.
"""
import numpy as np

def kl_mc(p_samples, q_samples):
    """
    Word-level unigram KL divergence MC estimator.
    Used for measuring semantic divergence.
    """
    # Simplified placeholder for the original logic
    # (The actual implementation was essentially unigram freq comparison)
    p_counts = {}
    for s in p_samples:
        for w in s.split():
            p_counts[w] = p_counts.get(w, 0) + 1
    
    q_counts = {}
    for s in q_samples:
        for w in s.split():
            q_counts[w] = q_counts.get(w, 0) + 1
            
    # Normalize
    p_total = sum(p_counts.values())
    q_total = sum(q_counts.values())
    
    kl = 0.0
    for w, c in p_counts.items():
        p_prob = c / p_total
        q_prob = q_counts.get(w, 0.5) / q_total # Minimal smoothing
        kl += p_prob * np.log(p_prob / q_prob)
    return max(0.0, kl)

def mdl_gzip(text):
    """Gzip byte length as a proxy for description length."""
    import gzip
    return len(gzip.compress(text.encode()))
