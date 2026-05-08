# Experiment 5: Diffusion-LM Dynamic Certificate

Purpose: extend the dual-certificate framework beyond ReAct scratchpads by
testing whether an intermediate LLaDA denoising latent has measurable decision
relevance for tool selection.

## Design

- Target model: local `LLaDA-8B-Instruct` diffusion LM.
- Visible trace: user tool-selection prompt and final tool-token distribution.
- Hidden channel: intermediate denoising block activation at a chosen diffusion
  step and transformer layer.
- Intervention certificate: inject Gaussian activation noise at the hidden
  channel and estimate the JS shift in final tool logits.
- Replay/ablation certificate: mask the hidden activation at the same channel
  and estimate the same JS shift.

The script follows the public LLaDA masked-diffusion sampling loop. It keeps the
final action token masked until the last step, so every condition is compared at
the same final tool slot.

## Run

Pilot:

```bash
python experiments/7.5_diffusion_certificate/run_llada_intervention.py \
  --model /Users/ostensible_paradox/models/LLaDA-8B-Instruct \
  --device auto \
  --dtype bfloat16 \
  --n-samples 5 \
  --steps 10 \
  --scratch-tokens 8 \
  --layer 1 \
  --intervention-step 9 \
  --perturbation gaussian:5.0 \
  --perturbation mask:1.0 \
  --out data/processed/diffusion_certificate/llada_intervention_k10_final.json
```

Full rebuttal run:

```bash
python experiments/7.5_diffusion_certificate/run_llada_intervention.py \
  --model /Users/ostensible_paradox/models/LLaDA-8B-Instruct \
  --device auto \
  --dtype bfloat16 \
  --n-samples 100 \
  --steps 10 \
  --scratch-tokens 8 \
  --layer 1 \
  --intervention-step 9 \
  --perturbation gaussian:5.0 \
  --perturbation mask:1.0 \
  --out data/processed/diffusion_certificate/llada_intervention_k10_final_full.json
```

## Output

The JSON output contains one entry per perturbation:

- `js_divergence_bits`: empirical lower-bound certificate.
- `ci_95_bits`: trajectory-block bootstrap interval.
- `wild_mean_dist` and `perturbed_mean_dist`: final distributions over
  `search`, `calculator`, `email`, `calendar`, `weather`.

The script redirects `HF_MODULES_CACHE` to `/tmp/llada_hf_modules` by default so
Transformers can load local LLaDA dynamic modules without writing into the
user's global HuggingFace cache.
