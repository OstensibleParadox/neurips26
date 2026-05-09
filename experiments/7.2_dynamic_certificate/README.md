# Dynamic Certificate Pipeline (§7.2)

Estimate the dynamic audit certificate
`δ_act^LB = max over admissible certificate classes`
for an open-weight agent model on a small tool-selection benchmark.

This is the pipeline backing Proposition B and Section 7.2 of the paper.

## Status

**Completed.** The pipeline supports full execution on Qwen2.5-7B-Instruct over a tool-selection benchmark. The paper reports pipeline results (0.0163 bits, Table 2).

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

## Files

```
README.md                       — this file
run_inference.py                — Qwen2.5-7B inference + activation capture
estimate_mi_infonce.py          — InfoNCE MI lower bound
estimate_mi_ce_diff.py          — CE-difference MI lower bound
estimate_mi_mine.py             — MINE fallback for broad probe
compute_delta_act_lb.py         — aggregates into δ_act^LB + bootstrap CI
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

## Expected output

A JSON record of the form:

```json
{
  "model": "Qwen2.5-7B-Instruct",
  "task": "tool_selection_5class",
  "probe": {"layer": 24, "type": "narrow_tool_vocab"},
  "N": 3000,
  "estimators": {
    "infonce":  {"delta_act_lb_bits": 0.XX, "ci_95": [0.XX, 0.XX]},
    "ce_diff":  {"delta_act_lb_bits": 0.XX, "ci_95": [0.XX, 0.XX]},
    "mine":     {"delta_act_lb_bits": 0.XX, "ci_95": [0.XX, 0.XX]}
  },
  "delta_act_lb_bits": 0.XX,
  "delta_act_lb_source": "infonce"
}
```

Paper-reported result: `0.0163` bits (InfoNCE), with the `2.32` bit ceiling
from `H(A_t) = log₂ 5`.
