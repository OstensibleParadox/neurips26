# Proxy CE-diff Diagnostics

## Summary

The original goal was to produce a dormant/active proxy CE-diff table with bootstrap CIs.
Instead, the diagnostic run exposed estimator pathologies that could produce false-positive
proxy certificates. The hardened v3 pipeline fixes these issues and treats the current
debug-scale result as valid non-certification.

**Updated Interpretation after V3 Positive Control:**
The debug-scale result of `δ_proxy_LB = 0` is a "valid non-certification / sanity gate" because the hardened v3 estimator has demonstrated statistical power on synthetic ground-truth data (see `experiments/7.4_synthetic_gt/V3_POSITIVE_CONTROL.md`). This confirms that when the estimator reports zero, it truly reflects a lack of detectable signal, rather than a lack of power.


## Pathologies Found

### 1. Permuted-Z oracle leakage

Earlier runs showed shuffled-label + permuted-Z reducing CE from ~0.91 to ~0.11,
producing an impossible +1.15 bit gap. This was traced to permutation alignment /
shared RNG structure between label shuffling and Z permutation.

Fix:
- independent RNGs for label shuffle and Z permutation;
- assert label_perm != z_perm;
- repeated null-suite gating.

### 2. PCA instability

PCA components differed across n_components due to nondeterministic solver behavior and
low effective rank.

Fix:
- use `PCA(..., svd_solver="full")`;
- check subspace stability instead of raw hash equality.

### 3. Task identity leakage

The debug set contains 200 samples but only 10 unique tasks. Sample-level CV leaks task
identity across folds.

Fix:
- use task-grouped CV;
- print train/test task counts;
- print missing-class diagnostics.

## v3 Result

At debug scale:
- n = 200 samples;
- unique tasks = 10;
- outer CV = 5 folds grouped by task;
- all null gates pass;
- all certified proxy lower bounds are 0.

This is valid non-certification.

## Interpretation

The result does not imply that the hidden state has no decision relevance.
It only means that the read-only proxy $Z$ does not provide a certified lower bound
under the current debug-scale, task-grouped evaluation. Positive dynamic evidence should
come from replay/intervention probes unless production-scale proxy experiments pass the
same sanity gate.

## Production Requirements

- unique tasks >= 100 minimum, preferably 300+;
- samples per task <= 5–10;
- StratifiedGroupKFold by task_id;
- no missing-class folds;
- dims = [1, 2, 3, 5, 8, 16];
- report:
  - raw_gap_bits;
  - null_p95_gap_bits;
  - null_corrected_gap_bits;
  - certified_delta_LB_bits.
