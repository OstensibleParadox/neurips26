# Experiment Pipeline — Dual Certificates for Agent Audit

Reproducibility guide for all experiments in the NeurIPS 2026 submission.

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install torch transformers scikit-learn pyyaml matplotlib numpy
```

Platform: Apple M4 Max (macOS). Replace `--device mps` with `--device cuda` or `--device cpu` as needed.

Model: `Qwen/Qwen2.5-7B-Instruct` (Apache 2.0, loaded via HuggingFace Transformers).

---

## Experiment 1: Static Certificate (§5.1)

**Purpose:** Compute $\varepsilon_\text{state}^\text{UB}$ from deployment topology via min-cut on unlogged channels.

### 1a. Extract DAG from a running agent

```bash
python experiments/7.1_static_certificate/extract_dag_from_agent.py \
    --model Qwen/Qwen2.5-7B-Instruct \
    --device mps \
    --out architectures/react_agent_extracted.json
```

### 1b. Enumerate cuts (diagnostic)

```bash
python experiments/7.1_static_certificate/enumerate_cuts.py \
    architectures/react_agent_extracted.json \
    --max-cuts 10 --all-edges
```

### 1c. Compute epsilon_UB (single logging level)

```bash
python experiments/7.1_static_certificate/compute_epsilon_ub.py \
    architectures/react_agent_extracted.json
```

### 1d. Run logging ablation (sweep)

```bash
python experiments/7.1_static_certificate/run_logging_ablation.py \
    --spec architectures/react_agent_extracted.json \
    --out data/processed/logging_ablation_extracted.json
```

**Expected output:** `data/processed/logging_ablation_extracted.json` with entries:
```
output_only:       16,464 bits  (bottleneck: scratchpad_read)
+log_router:       16,384 bits  (bottleneck: scratchpad_read)
+log_scratchpad:        0 bits  (none)
full_instrumentation:   0 bits  (none)
```

### 1e. Render figure

```bash
python experiments/7.1_static_certificate/render_figure.py \
    --results data/processed/logging_ablation_extracted.json \
    --spec architectures/react_agent_extracted.json
```

**Precomputed (included):** `data/processed/logging_ablation_extracted.json`

---

## Experiment 2: Dynamic Proxy Certificate (§5.2)

**Purpose:** Estimate $\delta_\text{act}^\text{LB}$ via observational proxy + CE-diff.

### 2a. Run inference (mixed tool-selection, 3000 trajectories)

```bash
python experiments/7.2_dynamic_certificate/run_inference.py \
    --config experiments/7.2_dynamic_certificate/configs/production.yaml
```

Captures:
- $\Phi_t$: layer-4 mean-pooled hidden states (visible trace representation)
- $Z_t$: layer-24 tool-vocab logit projection (proxy)
- $A_t$: tool action label (search/calculator/email/calendar/weather)

Output (generated, not pre-included): `data/processed/probe_pairs.pt`, `data/processed/probe_meta.json`

### 2b. Run proxy ablation (resolution sweep + controls)

```bash
python experiments/7.2_dynamic_certificate/run_proxy_ablation.py \
    --pairs data/processed/probe_pairs.pt \
    --meta data/processed/probe_meta.json \
    --predictor logistic_l2 \
    --out data/processed/proxy_ablation.json
```

Resolution levels: random (control), permuted (control), d=1/3/5/16/64/128 PCA, full proxy.

### 2c. Run dormant/active proxy split

Uses the same `CALCULATOR_TASKS` / `PLANNING_TASKS` prompts as Experiment 3.

```bash
python experiments/7.2_dynamic_certificate/run_proxy_dormant_active.py \
    --device mps \
    --n-samples 200 \
    --predictor logistic_l2 \
    --proxy-dim 64
```

Output: `data/processed/proxy_dormant_active.json`

**Expected output:**
```
dormant (calculator):    0.0000 bits  (single class, trivially zero)
active (planning):      ~0.04 bits    (positive but near observational floor)
```

### 2d. Render figure

```bash
python experiments/7.2_dynamic_certificate/render_figure_proxy.py \
    data/processed/proxy_ablation.json --out figures/proxy_ablation.pdf
```

**Precomputed (included):** `data/processed/proxy_ablation.json`, `data/processed/proxy_dormant_active.json`

---

## Experiment 3: Intervention & Replay Certificates (§5.3)

**Purpose:** Causal (Level 2) certificates via scratchpad perturbation and controlled replay.

### 3a. Run intervention (dormant + active)

```bash
python experiments/7.3_intervention/run_dormant_active.py \
    --config experiments/7.3_intervention/configs/production.yaml
```

Or run individually:

```bash
# Dormant (calculator — scratchpad irrelevant, JS ≈ 0)
python experiments/7.3_intervention/run_intervention.py \
    --config experiments/7.3_intervention/configs/production.yaml

# Active (planning — scratchpad drives behavior, JS > 0)
# Edit config: change task.name to "planning_search"
```

### 3b. Run controlled replay

```bash
python experiments/7.3_intervention/run_replay.py \
    --config experiments/7.3_intervention/configs/production.yaml
```

Output: `data/processed/intervention/replay_certificate.json`

### 3c. Render figure

```bash
python experiments/7.3_intervention/render_figure_intervention.py
```

**Precomputed (included):**
- `data/processed/intervention/intervention_calculator_only.json` — JS = 0 (dormant)
- `data/processed/intervention/intervention_planning_search.json` — JS > 0 (active)
- `data/processed/intervention/replay_certificate.json` — dormant/active contrast

---

## Experiment 4: Synthetic Ground-Truth Validation (§5.5)

**Purpose:** Validate that both certificates recover known hidden influence when the observational bottleneck is removed.

```bash
python experiments/7.4_synthetic_gt/run_synthetic.py \
    --n-trajectories 1000 \
    --beta-levels 0.0 0.5 1.0 2.0 4.0 \
    --out-dir data/processed/synthetic
```

**Expected output:**
```
beta=0.0: true_MI=0.0000 bits, delta^LB≈0 bits, eps^UB=1.0 bits
beta=0.5: true_MI≈0.12 bits, delta^LB≈0.05 bits, eps^UB=1.0 bits
beta=1.0: true_MI≈0.31 bits, delta^LB≈0.20 bits, eps^UB=1.0 bits
beta=2.0: true_MI≈0.50 bits, delta^LB≈0.40 bits, eps^UB=1.0 bits
beta=4.0: true_MI≈0.72 bits, delta^LB≈0.65 bits, eps^UB=1.0 bits
```

$\delta_\text{act}^\text{LB}$ tracks the true $I(S_t; A_t \mid \tilde T_t)$ from below at all non-trivial $\beta_h$.

Results are generated by the pipeline above; no precomputed synthetic results are included (the experiment is self-contained and deterministic).

---

## Experiment 5: Diffusion-LM Intervention/Replay Certificate (§5.6)

**Purpose:** Test dynamic certificates on a diffusion LM by perturbing an intermediate LLaDA denoising latent during tool selection.

```bash
python experiments/7.5_diffusion_certificate/run_llada_intervention.py \
    --model path/to/LLaDA-8B-Instruct \
    --device auto \
    --dtype bfloat16 \
    --n-samples 20 \
    --steps 10 \
    --scratch-tokens 8 \
    --layer 1 \
    --control-layer 32 \
    --probe-steps 2,4,6,8,10 \
    --perturbation gaussian:5.0 \
    --out data/processed/diffusion_certificate/llada_temporal_k10.json
```

Gaussian perturbation at layer 1 is the intervention certificate, profiled across denoising steps $\{2,4,6,8,10\}$. Layer 32 perturbation serves as a specificity control. Output reports per-step JS divergence in bits with bootstrap CIs over the final tool-token distribution.

---

## Full Pipeline (one-shot)

```bash
# 1. Static certificate
python experiments/7.1_static_certificate/extract_dag_from_agent.py \
    --model Qwen/Qwen2.5-7B-Instruct --device mps \
    --out architectures/react_agent_extracted.json
python experiments/7.1_static_certificate/run_logging_ablation.py \
    --spec architectures/react_agent_extracted.json \
    --out data/processed/logging_ablation_extracted.json

# 2. Proxy certificate (mixed dataset)
python experiments/7.2_dynamic_certificate/run_inference.py \
    --config experiments/7.2_dynamic_certificate/configs/production.yaml
python experiments/7.2_dynamic_certificate/run_proxy_ablation.py \
    --pairs data/processed/probe_pairs.pt \
    --meta data/processed/probe_meta.json \
    --predictor logistic_l2 \
    --out data/processed/proxy_ablation.json

# 3. Intervention certificate
python experiments/7.3_intervention/run_dormant_active.py \
    --config experiments/7.3_intervention/configs/production.yaml

# 4. Synthetic validation
python experiments/7.4_synthetic_gt/run_synthetic.py \
    --n-trajectories 1000 --out-dir data/processed/synthetic

# 5. Diffusion-LM temporal certificate profile
python experiments/7.5_diffusion_certificate/run_llada_intervention.py \
    --model path/to/LLaDA-8B-Instruct \
    --n-samples 20 \
    --steps 10 \
    --probe-steps 2,4,6,8,10 \
    --control-layer 32 \
    --out data/processed/diffusion_certificate/llada_temporal_k10.json

# 6. Multi-agent private-report dynamic certificate
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
    --n-per-class 200 \
    --k-samples 8 \
    --workers 3 \
    --out-dir data/processed/multi_agent_certificate
```

---

## Data Inventory

Files marked **included** ship in this archive. Files marked **generated** are produced by running the pipeline.

| Path | Status | Description | Used By |
|------|--------|-------------|---------|
| `data/tool_selection/*.txt` | included | 3000 tool-selection queries (600 per class) | §5.2 proxy (mixed) |
| `data/processed/logging_ablation_extracted.json` | included | Static certificate ablation | Table 1 |
| `data/processed/proxy_ablation.json` | included | Resolution ablation results | Table 2 |
| `data/processed/proxy_dormant_active.json` | included | Dormant/active proxy split | Table 2 |
| `data/processed/intervention/*.json` | included | Intervention & replay results | Tables 3–4 |
| `data/processed/diffusion_certificate/llada_temporal_k10.json` | included | LLaDA temporal certificate profile (per-step JS divergence) | §5.6 |
| `data/processed/multi_agent_certificate/*` | generated | Multi-agent private-report reports, controller samples, JS summary | §5.7 |
| `data/processed/probe_pairs.pt` | generated | $(\Phi_t, Z_t, A_t)$ tensor pairs | §5.2 CE-diff estimation |
| `data/processed/probe_meta.json` | generated | Probe metadata (labels, dims) | §5.2 |
| `data/processed/synthetic/` | generated | Synthetic ground-truth results | §5.5 |

Additional raw data files (`data/proxy_planning/`, `data/proxy_injected/`, `data/episodes/`) are not included; the precomputed results above cover Tables 1–4. The proxy planning/injected trajectories are regenerated on-the-fly by `run_proxy_dormant_active.py`.

## Architecture Specs

Included in `experiments/7.1_static_certificate/architectures/`:

| File | Description |
|------|-------------|
| `react_agent.json` | Original ReAct agent DAG spec |
| `react_agent_extracted.json` | Extracted DAG from live Qwen2.5-7B agent |
| `diffusion_lm.json` | Diffusion-LM deployment spec |
| `multi_agent_scratchpad.json` | Multi-agent deployment spec |
| `multi_agent_ollama.json` | Two-agent Ollama deployment spec |
| `llada_8b_instruct.json` | LLaDA-8B-Instruct deployment spec |
