# Dynamic Certificate Pipeline (§7.2)

Estimate the dynamic audit certificate
`δ_act^LB = max over admissible certificate classes`
for an open-weight agent model on a small tool-selection benchmark.

This is the pipeline backing Proposition B and Section 7.2 of the paper.

## Status

**Completed.** The pipeline supports full execution on Qwen2.5-7B-Instruct over
a tool-selection benchmark. The checked-in ReAct replay headline used by the
paper is tracked in `data/processed/intervention/replay_certificate.json` and
rendered through `experiments/render_paper_tables.py`.

## Model

**Qwen2.5-7B-Instruct** (Apache 2.0, open weights, strong native tool use).
Served via HuggingFace transformers with the forward-pass layer-`L` residual
stream exposed as a hook. Runs on Apple M4 Max with 4-bit or 8-bit
quantization via bitsandbytes or MLX.

Alternatives considered (Llama-3.1-8B-Instruct, Mistral-7B-Instruct) were
rejected for weaker native agent behaviour; Qwen2.5-7B is the default.

## Task

**Tool selection.** For each observation, the agent emits one of 5 actions:

- `calculator`
- `search`
- `email`
- `calendar`
- `weather`

The 5-class action space gives an entropy ceiling of
`log2 5 ≈ 2.32 bits`, which serves as the upper reference for
`δ_act^LB` values.

## Probe

**Primary (narrow).** Last-layer residual stream projected onto the tool-use
vocabulary subspace:

```
Z_t = W_U[T_vocab] @ h_t^{(L)}
```

where:

- `h_t^{(L)}` is the layer-`L` residual stream at the final position of the
  prompt (L = 24 for Qwen2.5-7B-Instruct, out of 28 layers).
- `W_U` is the unembedding matrix (shape `[vocab, d_model]`, with
  `d_model = 3584` for Qwen2.5-7B-Instruct).
- `T_vocab ⊆ vocab` is a curated tool-use token subset: `"calculator"`, `"search"`,
  `"email"`, `"calendar"`, `"weather"`, `"{"`, `"call"`, `"tool"`, and model-
  specific special tool tokens (target size 50-200 tokens).
- `Z_t` is a low-dimensional vector in the tool-use subspace, suitable for
  tractable MI estimation.

Because `Z_t = φ(h_t^{(L)})` is a deterministic function of the internal
state, the coarsening-DPI bound of Proposition B(2) applies directly.

**Fallback (broad).** If the narrow probe yields `δ_act^LB ≈ 0`, re-run with
`Z_t = h_t^{(L)}` (full residual stream) and the MINE estimator. Reported in
parallel to the narrow probe in the paper.

## Estimators

All three are valid lower-bound estimators of `I(Z_t; A_t | T̃_t)`, and the
max of the three is a valid `δ_act^LB`.

1. **InfoNCE** (primary, `estimate_mi_infonce.py`)
   - `I^LB = log N - L_InfoNCE`
   - Two-layer MLP critic, temperature 0.1, batch size 256.
   - Bootstrap 95% CI via 1000 resamples.

2. **CE difference** (sanity check, `estimate_mi_ce_diff.py`)
   - `I^LB = H(A_t) - CE(A_t | Z_t)`
   - Logistic regression for `p(A_t | Z_t)`.
   - Fast, interpretable, serves as floor estimator.

3. **MINE** (fallback for broad probe, `estimate_mi_mine.py`)
   - Variational donsker-varadhan bound with a neural critic.
   - Used only if the narrow probe is underpowered.

## Methodology note (May 2026)

The CE-difference estimator is sanity-hardened via `diagnose_v3.py`:
- **StratifiedGroupKFold** outer CV (no task leakage across train/test splits)
- **Group-aware inner CV** via GridSearchCV + GroupKFold (C selection clean)
- **Independent RNG seeds** for label-shuffle vs Z-permutation controls
- **Deterministic PCA** (`svd_solver="full"`) + subspace angle stability check
- **Repeated null suite** (B=20–100 label shuffles) → null p95 → null-corrected gap
- **Per-fold generalization diagnostics** (missing classes, uniform/prior CE baselines)

Null gate: any null control with |gap| > 0.5 bits → pipeline invalid for that condition.
Conservative certificate: `δ_act^LB = max(0, raw_gap − null_p95)`.

At debug scale (N=200, 10 unique tasks), per-fold missing-class warnings are expected
and resolve naturally at production scale (N≥3000, ≥300 unique tasks).

## Files

```
README.md                       — this file
run_inference.py                — Qwen2.5-7B inference + activation capture
estimate_mi_infonce.py          — InfoNCE MI lower bound
estimate_mi_ce_diff.py          — CE-difference MI lower bound
estimate_mi_mine.py             — MINE fallback for broad probe
compute_delta_act_lb.py         — aggregates into δ_act^LB + bootstrap CI
diagnose_v3.py                  — sanity-hardened proxy CE-diff pipeline
                                  (StratifiedGroupKFold, null suite, fold diagnostics)
diagnose_v2.py                  — earlier version (kept for reference; use v3)
diagnose_proxy_dim.py           — original proxy-dim sweep (v1, has PCA leakage)
run_proxy_ablation.py           — proxy resolution ablation sweep
run_proxy_dormant_active.py     — dormant (calculator) vs active (planning) split
render_figure_proxy.py          — render proxy ablation figure
configs/
  qwen25_7b_tool_sel.yaml       — probe layer, T_vocab spec, sample count
  infonce_critic.yaml           — InfoNCE critic architecture
__init__.py                     — empty, makes directory importable
```

## Usage

```bash
python run_inference.py \
    --config configs/qwen25_7b_tool_sel.yaml \
    --out data/processed/qwen25_probe_pairs.pt

python estimate_mi_infonce.py \
    --pairs data/processed/qwen25_probe_pairs.pt \
    --critic configs/infonce_critic.yaml \
    --out data/processed/infonce_result.json

python estimate_mi_ce_diff.py \
    --pairs data/processed/qwen25_probe_pairs.pt \
    --out data/processed/ce_diff_result.json

python compute_delta_act_lb.py \
    --infonce data/processed/infonce_result.json \
    --ce-diff data/processed/ce_diff_result.json \
    --out data/processed/delta_act_lb.json
```

## Expected output (debug scale)

When running `run_proxy_dormant_active.py` at debug scale ($N=200$, 10 unique tasks):

```json
{
  "calculator_dormant": {"delta_act_lb_bits": 0.0, "ci_95": [0.0, 0.0]},
  "planning_active":    {"delta_act_lb_bits": 0.0, "ci_95": [-0.11, -0.06]},
  "planning_perturbed": {"delta_act_lb_bits": 0.0, "ci_95": [-0.07, 0.13]}
}
```

**Interpretation:**
- All certified lower bounds are clipped to zero (**valid non-certification**).
- Negative raw gaps (e.g., `-0.09` bits for `planning_active`) are estimator
  variance/bias artifacts, not negative information.
- The `~0.04` bits point estimate for `planning_perturbed` is not certified
  because its 95% CI straddles zero.

Paper-reported ReAct replay effect sizes are now checked in under
`data/processed/intervention/`. The `2.32` bit ceiling from
$H(A_t) = \log_2 5$ remains the action-space reference. Debug-scale results
using the hardened `diagnose_v3.py` pipeline serve as a sanity gate, not an
effect-size measurement.

**Updated Interpretation after V3 Positive Control:**
The debug-scale result of `δ_proxy_LB = 0` is a "valid non-certification / sanity gate" because the hardened v3 estimator has demonstrated statistical power on synthetic ground-truth data (see `experiments/7.4_synthetic_gt/V3_POSITIVE_CONTROL.md`). This confirms that when the estimator reports zero, it truly reflects a lack of detectable signal, rather than a lack of power.
