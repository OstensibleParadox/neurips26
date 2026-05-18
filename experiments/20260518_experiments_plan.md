# Task: Run the v3 estimator positive control on synthetic ground-truth data

  You are working in the repo `/Users/ostensible_paradox/Documents/output_only`
  (Paper 4, NeurIPS submission #1749, "Dual Certificates for Agent Audit").
  Run all commands from the repo root. macOS, Python venv with
  numpy/torch/scikit-learn/matplotlib already available.

  ## Background (read this — it determines what counts as success)

  The paper's framework has three certificates: intervention, replay, and proxy.
  The proxy certificate estimates I(Z; A | T̃) — residual decision relevance of a
  read-only hidden-state proxy Z, beyond what the visible trace T̃ explains.

  On 2026-05-15 a leakage bug was found in the original proxy estimator: the
  null control used the SAME RNG seed for label-shuffle and Z-permutation, so the
  null gate gave false positives and the estimator was effectively not working.
  It was rewritten as a hardened "v3" estimator in
  `experiments/7.2_dynamic_certificate/diagnose_v3.py` (independent RNGs,
  StratifiedGroupKFold, deterministic PCA, repeated null suite, conservative
  clipping `delta_LB = max(0, raw_gap - null_p95)`).

  At production scale the proxy path certifies δ_proxy_LB = 0. That is a *valid
  non-certification* IF AND ONLY IF the v3 estimator actually has statistical
  power. The experiment that establishes power is the **synthetic positive
  control**: `experiments/7.4_synthetic_gt/run_synthetic.py` generates data with
  KNOWN ground-truth I(H; A | T̃) > 0. A working estimator must certify > 0 there.

  **Two outcomes are pre-registered and BOTH are valid, publishable findings:**
  - v3 certifies > 0 on synthetic at β_h ∈ {1,2,4} → estimator has power; the
    production δ_proxy_LB = 0 is a true null.
  - v3 also certifies 0 on synthetic → the estimator has a power problem; this is
    a separate finding to report honestly.

  Your job is to RUN this control and REPORT whatever happens. It is NOT to make
  the result come out positive.

  ## Current state (verify, don't trust blindly — read the files first)

  - `experiments/7.4_synthetic_gt/run_synthetic.py` still uses the OLD pre-v3
    estimator `ce_diff_estimate(T, H, A, n_classes, n_folds=5)` (plain
    RandomState(42) 5-fold, fresh MLP per fold). It has never been updated.
  - `experiments/7.2_dynamic_certificate/diagnose_v3.py` is a standalone script,
    imported by nothing. Its live-capture entrypoint `capture_one_condition`
    needs a Qwen model and is NOT usable for synthetic. The reusable parts are
    the pure helpers and the null-suite logic.
  - `data/processed/synthetic/` does not exist. This control has never been run.
  - Docs `experiments/7.2_dynamic_certificate/README.md` and
    `.../PROXY_DIAGNOSTICS.md` already assert the debug-scale result is a
    "valid non-certification / sanity gate" — a claim that logically depends on
    this control, which has not been run.

  ## Key technical facts (confirm by reading the two files)

  `run_synthetic.py`:
  - `generate_data(n, d_tilde=8, n_classes=5, beta_h, seed=42)` returns
    `T (n,8) float`, `H (n,) binary float`, `A (n,) int`, `probs`, `true_mi`
    (in nats). `true_mi_bits = true_mi / ln 2`.
  - `main(n_trajectories, beta_levels, out_dir, skip_plot)` writes
    `<out_dir>/synthetic_results.json` (+ pdf). Default out_dir
    `data/processed/synthetic`.

  `diagnose_v3.py`:
  - Constants: `DIMS=[1,2,3,5,8,16]`, `PHI_PCA_DIM=128`, `N_NULL_REPEATS=20`,
    `CS_GRID=[0.001,0.01,0.1,1.0,10.0]`, independent `SEED_LABEL` / `SEED_ZPERM`.
  - `_make_outer_folds(A, task_ids, rng_seed)` → StratifiedGroupKFold, KFold
    fallback if too few groups.
  - `_eval_one(Z_raw, Phi_raw, A_in, task_ids, dim_z, z_desc, folds, rng_seed)`
    → dict; `gap_bits = (ce_trace - ce_proxy)/ln2`. trace model = LogReg on
    PCA(Phi); proxy model = LogReg on concat[PCA(Phi), PCA(Z)]; inner CV =
    GroupKFold(groups=task_ids); GridSearchCV over CS_GRID; PCA svd_solver="full".
  - `run_condition` (≈ lines 314–415) contains the repeated null suite — read it
    and reproduce its algorithm exactly.

  Semantic mapping (verify it holds): v3's "trace vs trace+proxy" split is exactly
  synthetic's "T vs T+H". So `Phi_raw = T`, `Z_raw = H.reshape(-1,1)`,
  `A_in = A`. Then `gap_bits` = CE(T) − CE(T,H) = an estimate of the synthetic
  estimand I(H; A | T̃). Confirm this correspondence before proceeding; if it
  does not hold, STOP and report why.

  Synthetic data has NO task structure (T is i.i.d. Gaussian, H i.i.d.
  Bernoulli). v3's task-grouped CV therefore has nothing to group on. Use
  per-sample singleton groups `task_ids = np.arange(n)` (StratifiedGroupKFold /
  GroupKFold then degrade to standard stratified/k-fold — the honest
  representation of "no task structure"). Document this choice in the output and
  the findings file; do not pretend there is task grouping.

  Z is 1-dimensional, so DIMS clamps to dim_z=1 for every entry. Use dim_z=1
  only; do not sweep dims (it is meaningless here and say so).

  ## What to implement

  1. Read `run_synthetic.py` and `diagnose_v3.py` end to end first.
  2. Add a v3 estimator path WITHOUT deleting the legacy one. Either:
     (a) import the pure helpers from diagnose_v3 (preferred, DRY), or
     (b) if importing has heavy/unsafe side effects, copy only the needed
         functions into a new module
  `experiments/7.4_synthetic_gt/synthetic_v3_estimator.py`
         with a header comment citing the source path and current git commit.
     Add a `--estimator {legacy,v3}` CLI flag to run_synthetic.py defaulting to
     `legacy` (keeps existing behavior/regression-safe). The v3 path must:
     - map T→Phi, H.reshape(-1,1)→Z, A→A_in, task_ids=np.arange(n);
     - build outer folds via the v3 fold helper;
     - compute raw_gap via the v3 per-fold CE-diff at dim_z=1;
     - run the repeated null suite EXACTLY as in `run_condition`:
       for b in range(N_NULL_REPEATS): label-shuffle A with
       RandomState(SEED_LABEL+b); gaussian-Z null = randn(N,1) with
       RandomState(rng_seed+b); permuted-Z null =
       default_rng(SEED_ZPERM + b*100).permutation(Z, axis=0); collect both
       gap lists; `null_p95 = max(pctl(gauss,95), pctl(perm,95))`;
       `null_pass = max(max|gauss|, max|perm|) < 0.5`;
     - `certified_delta_LB_bits = max(0.0, raw_gap - null_p95)` if null_pass
       else null (pipeline invalid for that β).
  3. Run the control with the v3 path over
     `beta_levels = [0.0, 0.5, 1.0, 2.0, 4.0]` (0.0 and 0.5 are the in-script
     negative/low controls; 1.0/2.0/4.0 are the positive control of record).
     Use `n_trajectories = 2000` and the fixed default seeds. Also run the
     LEGACY estimator on the identical data for an apples-to-apples comparison.
  4. Write `data/processed/synthetic/synthetic_results_v3.json` (do NOT overwrite
     the legacy `synthetic_results.json`). Per β record:
     `beta_h, true_mi_bits, raw_gap_bits, null_p95_bits,
     null_corrected_gap_bits, certified_delta_LB_bits, null_pass,
     legacy_delta_lb_bits, n, n_null_repeats, n_classes, task_grouping:"singleton"`.
     Print a comparison table to stdout.

  ## Honest-reporting deliverable

  Write `experiments/7.4_synthetic_gt/V3_POSITIVE_CONTROL.md` containing:
  - the command(s) you ran and the exact resulting numbers (must match the JSON
    on disk — no numbers that aren't from a run you actually executed);
  - which pre-registered branch occurred (power confirmed vs power problem),
    decided strictly by: does `certified_delta_LB_bits > 0` hold at β_h ∈
    {1,2,4} with `null_pass = true`;
  - the v3-vs-legacy comparison;
  - proposed doc edits as explicit BEFORE/AFTER blocks (do not silently rewrite)
    for the "sanity gate / valid non-certification" wording in
    `experiments/7.2_dynamic_certificate/README.md` and `PROXY_DIAGNOSTICS.md`,
    written for whichever branch actually occurred. Apply the edits only after
    showing the before/after in the md file.
  - An observations section. While reading `generate_data`/`_mc_mi`, note any
    inconsistency you find (e.g. whether the MC true-MI uses the same noise model
    as the sampled data). REPORT such issues; do NOT silently change the
    ground-truth computation — altering the GT is moving the goalposts.

  ## Hard guardrails — read twice

  - The result is whatever the run produces. Both branches are valid. Do NOT
    tune seeds, β, n, dims, CS_GRID, N_NULL_REPEATS, fold count, PCA settings,
    or estimator internals to push δ_LB above 0. If v3 certifies 0 on synthetic,
    that IS the finding ("estimator power problem") — report it plainly.
  - You may run at most ONE additional pre-declared robustness point
    (n=4000 with the same code) and you must report it whether or not it agrees
    with n=2000. No best-of selection. No silent retries with different configs.
  - Every number in the .md must trace to the JSON file you wrote. No fabricated
    or "expected" numbers.
  - Do not modify `run_synthetic.py`'s legacy `ce_diff_estimate`. Do not touch
    `experiments/7.1/7.3/7.5/7.6`, the `auditbench/` pipeline, or any
    `data/processed/` outputs other than the new synthetic v3 files.
  - If the semantic mapping (T↔Phi, H↔Z) does not actually hold once you read
    the code, STOP and report instead of forcing it.

  ## Deliverables checklist

  - [ ] `run_synthetic.py` with non-destructive `--estimator {legacy,v3}` flag
        (+ optional `synthetic_v3_estimator.py`)
  ## Deliverables checklist

  - [ ] `run_synthetic.py` with non-destructive `--estimator {legacy,v3}` flag
        (+ optional `synthetic_v3_estimator.py`)
  - [ ] `data/processed/synthetic/synthetic_results_v3.json` on disk
  - [ ] `experiments/7.4_synthetic_gt/V3_POSITIVE_CONTROL.md` with real numbers,
        branch determination, v3-vs-legacy comparison, before/after doc edits,
        observations
  - [ ] Doc edits applied to 7.2 README.md + PROXY_DIAGNOSTICS.md matching the
        actual branch, only after before/after shown
  - [ ] Legacy path still runs unchanged (`--estimator legacy` reproduces prior
        behavior)
