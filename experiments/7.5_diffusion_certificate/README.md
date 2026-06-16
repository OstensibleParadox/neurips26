# Experiment 5: Diffusion-LM Dynamic Certificate

Purpose: extend the dual-certificate framework beyond ReAct scratchpads by
profiling $\delta_\text{act}^\text{LB}$ across the temporal dimension of LLaDA's
$K$-step denoising trajectory.

## Design

- Target model: local `LLaDA-8B-Instruct` diffusion LM.
- Visible trace: user tool-selection prompt and final tool-token distribution.
- Hidden channel: layer-1 block activation at intermediate denoising steps.
- Temporal profiling: Gaussian perturbation ($\sigma{=}5.0$) applied at steps
  $\{2,4,6,8,10\}$; layer 31 perturbation as specificity control.
- $n{=}20$ trajectories per step, trajectory-block bootstrap with $1{,}000$
  resamples.

The observed pattern is "late-binding": $\delta_\text{act}^\text{LB}$ is near
zero at step 2 (noise-dominated), and peaks at step 10 (token refinement). The
checked-in values are in
`data/processed/diffusion_certificate/llada_temporal_k10.json` and `.csv`.

## Run

```bash
python experiments/7.5_diffusion_certificate/run_llada_intervention.py \
  --model path/to/LLaDA-8B-Instruct \
  --device auto \
  --dtype bfloat16 \
  --n-samples 20 \
  --steps 10 \
  --scratch-tokens 8 \
  --layer 1 \
  --control-layer 31 \
  --probe-steps 2,4,6,8,10 \
  --perturbation gaussian:5.0 \
  --out data/processed/diffusion_certificate/llada_temporal_k10.json
```

## Output

The JSON output contains per-step results for target and control layers:

- `js_divergence_bits`: empirical lower-bound certificate at each step.
- `ci_95_bits`: trajectory-block bootstrap interval.
- `wild_mean_dist` and `perturbed_mean_dist`: final distributions over
  `search`, `calculator`, `email`, `calendar`, `weather`.

The runner also writes `data/processed/diffusion_certificate/llada_temporal_k10.csv`
as a compact per-step summary for paper-table generation.

The script redirects `HF_MODULES_CACHE` to `/tmp/llada_hf_modules` by default so
Transformers can load local LLaDA dynamic modules without writing into the
user's global HuggingFace cache.
