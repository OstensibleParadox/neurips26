# Experiments: Research Reset

> **Current status: pre-gate / INCONCLUSIVE.** The active research program is
> the 8.x transcript-insufficiency gate. The 7.x material below is a legacy
> reproduction guide, not the current expansion roadmap.

See [`../README_NEW_DIRECTION.md`](../README_NEW_DIRECTION.md) for the research
specification and [`../GO_NO_GO.md`](../GO_NO_GO.md) for thresholds, canonical
evidence paths, and the current decision.

## Active 8.x Gate Work

- [`8.1_tracetwin/`](8.1_tracetwin/) — exact mediated/bypass passive twins,
  controlled-clamp calibration, finite-sample validity, and passive-baseline
  failure.
- [`8.2_sequential_certificate/`](8.2_sequential_certificate/) — predictable
  decoder e-processes, adaptive probes, and optional stopping; the simulator
  upper certificate remains a gate TODO.
- [`8.3_agentdojo/`](8.3_agentdojo/) — natural on-support private-state swaps at
  a consequential structured-action boundary, with trace clamping and strict
  negative controls.

These workstreams are gate experiments. Their presence does not imply that any
GO criterion has passed. New evidence should use the canonical destinations
under `data/processed/8.1_tracetwin/`,
`data/processed/8.2_sequential_certificate/`, and
`data/processed/8.3_agentdojo/` listed in `GO_NO_GO.md`.

## Experiment Boundary Matrix

| Directory | Status | Rule |
|---|---|---|
| `8.1_tracetwin/` | **Active** | Implement and calibrate the exact laboratory. |
| `8.2_sequential_certificate/` | **Active** | Implement and validate the sequential certificate. |
| `8.3_agentdojo/` | **Active** | Implement the real structured-action gate experiment. |
| `7.3_intervention/` | **Reusable infrastructure** | Reuse replay/intervention and discrete-action evaluation code; primary evidence must remain on support and transcript preserving. |
| `7.4_synthetic_gt/` | **GT repaired; historical results quarantined** | Reuse the tested noise-consistent ground-truth calculation only; regenerate and review estimator outputs before treating this experiment as validation. |
| `7.1_static_certificate/` | **Frozen legacy** | Historical reproduction only; no code, config, documentation, or experiment extension. |
| `7.2_dynamic_certificate/` | **Frozen legacy** | Historical reproduction only; no code, config, documentation, or experiment extension. |
| `7.5_diffusion_certificate/` | **Frozen legacy** | Historical reproduction only; no code, config, documentation, or experiment extension. |
| `7.6_multi_agent_certificate/` | **Frozen legacy** | Historical reproduction only; no code, config, documentation, or experiment extension. |

Shared trace and utility code in `../src/` remains reusable. Processed artifacts
needed to reproduce old pilot results must be preserved, but legacy outputs are
not evidence that the new gate passed.

## Gate-Quality Evaluation Rules

- Randomize admissible probes exogenously at the declared boundary.
- Use exact clamping or predeclared structured-trace equivalence for primary
  evidence.
- Evaluate discrete, safety-relevant deployed actions, not only next-token
  logits.
- Use paired task-block bootstrap or randomization inference.
- Treat zero, blank, Gaussian, and arbitrary-text interventions as cautionary
  baselines only.
- Report active, visible-twin, dormant, disconnected, same-class, full-logging,
  transcript-monitor, and marginal-rate controls separately.
- Do not infer decoder-independent non-recoverability from failure of one
  trained classifier.

---

# Legacy 7.x Reproduction Guide

The remainder of this file is preserved to reproduce the abandoned
latent-state/capacity-map paper. It is **legacy documentation**. Commands under
frozen directories must not be extended or used as the active research plan;
the boundary matrix above takes precedence.

Reproducibility guide for the legacy Dual Certificates security-paper
experiments.

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install torch transformers scikit-learn pyyaml matplotlib numpy
```

Platform: Apple M4 Max (macOS). Replace `--device mps` with `--device cuda` or `--device cpu` as needed.

Model: `Qwen/Qwen2.5-7B-Instruct` (Apache 2.0, loaded via HuggingFace Transformers).

---

## Experiment 1: Static Certificate (§6.1)

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

## Experiment 2: Dynamic Proxy Certificate (Appendix B)

**Purpose:** Estimate $\delta_\text{act}^\text{LB}$ via observational proxy + CE-diff.

**Sanity check:** `diagnose_v3.py` validates the proxy pipeline at debug scale before
cluster runs — StratifiedGroupKFold, null suite gating, per-fold generalization
diagnostics. See `experiments/7.2_dynamic_certificate/README.md` for details.

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

**Debug-scale sanity result (`diagnose_v3.py`):**
```
calculator / dormant: certified proxy dLB = 0
planning / vanilla:   certified proxy dLB = 0
planning / perturbed: certified proxy dLB = 0
wrong-module control: certified proxy dLB = 0
```
Interpretation: this is valid non-certification, not negative mutual information.
After fixing permutation leakage, enforcing task-grouped CV, and applying repeated
null-suite gating, the read-only proxy CE-diff probe does not provide a positive
dynamic certificate at debug scale. Production-scale proxy runs require many more
unique tasks and should report raw_gap_bits, null_corrected_gap_bits, and
certified_delta_LB_bits separately.

### 2d. Render figure

```bash
python experiments/7.2_dynamic_certificate/render_figure_proxy.py \
    data/processed/proxy_ablation.json --out figures/proxy_ablation.pdf
```

**Precomputed (included):** `data/processed/proxy_ablation.json`, `data/processed/proxy_dormant_active.json`

---

## Experiment 3: Intervention & Replay Certificates (§6.2)

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

### 3c. Boundary-mined argmax replay validation

Ordinary ReAct prompts are often far from the tool-decision boundary, so the
scratchpad can change soft probabilities without changing argmax tool counts.
Boundary mining first scores wild scratchpad prompts by top-1/top-2 tool-logit
margin, keeps low-margin prompts, then evaluates scratchpad remove / neutral /
counterfactual conditions on that boundary set.

```bash
python experiments/7.3_intervention/run_boundary_replay.py \
    --config experiments/7.3_intervention/configs/boundary_replay.yaml \
    --max-candidates 5000 \
    --margin-threshold 0.5 \
    --top-k-boundary 500
```

Zero-dependency dry-run candidate generation:

```bash
python3 experiments/7.3_intervention/run_boundary_replay.py \
    --dry-run \
    --max-candidates 25 \
    --output-dir /tmp/boundary_replay_smoke
```

Output: `data/processed/intervention_boundary/boundary_summary.json`.
If positive, report this as module-level realized-action validation for ReAct;
do not replace the multi-agent result as the main realized-action headline.
The same script accepts `--candidates-jsonl data/react_boundary_candidates.jsonl`
for mining a real task pool instead of the generated ambiguous pool.

### 3d. Render figure

```bash
python experiments/7.3_intervention/render_figure_intervention.py
```

**Precomputed (included):**
- `data/processed/intervention/intervention_calculator_only.json` — JS = 0 (dormant)
- `data/processed/intervention/intervention_planning_search.json` — JS > 0 (active)
- `data/processed/intervention/replay_certificate.json` — dormant/active contrast

`run_dormant_active.py` also emits raw per-sample tool distributions under
`data/processed/intervention/raw/intervention_*_samples.jsonl`; rerun
`recompute_intervention_summary.py` to rebuild the aggregate JSON/CSV from
those rows. Existing aggregate files mark these raw paths as
`regenerate_required` when the raw rows are not present.

---

## Experiment 4: Synthetic Ground-Truth Validation (Appendix E)

**Historical status: withdrawn pending regenerated estimator results.** The
noise-consistent ground-truth engine is repaired and tested, but the old tables
and the claim that an estimator tracked a lower bound are not valid v2
evidence. See `7.4_synthetic_gt/README.md`.

```bash
python3 experiments/7.4_synthetic_gt/run_synthetic.py \
    --ground-truth-only \
    --n-trajectories 1000 \
    --beta-levels 0.0 0.5 1.0 2.0 4.0 \
    --noise-std 0.1 \
    --gt-inner-samples 8192 \
    --out-dir /tmp/synthetic_gt_repaired
```

This writes a separate `synthetic_ground_truth.json`. Do not run the legacy or
v3 estimator path as validation until its statistical claim has been reviewed
against the repaired target.

---

## Experiment 5: Diffusion-LM Intervention/Replay Certificate (§6.3)

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
    --control-layer 31 \
    --probe-steps 2,4,6,8,10 \
    --perturbation gaussian:5.0 \
    --out data/processed/diffusion_certificate/llada_temporal_k10.json
```

Gaussian perturbation at layer 1 is the intervention certificate, profiled across denoising steps $\{2,4,6,8,10\}$. Layer 32 perturbation serves as a specificity control. Output reports per-step JS divergence in bits with bootstrap CIs over the final tool-token distribution.

---

## Experiment 6: Multi-Agent Private-Report

**Purpose:** Measure how private worker reports influence controller decisions under
different communication topologies.

```bash
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
    --n-per-class 200 \
    --k-samples 8 \
    --workers 3 \
    --out-dir data/processed/multi_agent_certificate
```

**Precomputed (included):** `data/processed/multi_agent_certificate/summary.json`,
`data/processed/multi_agent_certificate/summary.csv`. Full per-task reports and
controller samples are generated by rerunning the command above.

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

# 2. Proxy certificate (sanity check first, then production)
python experiments/7.2_dynamic_certificate/diagnose_v3.py
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
python experiments/7.3_intervention/recompute_intervention_summary.py \
    --out-dir data/processed/intervention

# 4. Synthetic validation
python3 experiments/7.4_synthetic_gt/run_synthetic.py \
    --ground-truth-only --n-trajectories 1000 \
    --gt-inner-samples 8192 --out-dir /tmp/synthetic_gt_repaired

# 5. Diffusion-LM temporal certificate profile
python experiments/7.5_diffusion_certificate/run_llada_intervention.py \
    --model path/to/LLaDA-8B-Instruct \
    --n-samples 20 \
    --steps 10 \
    --probe-steps 2,4,6,8,10 \
    --control-layer 31 \
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
| `data/tool_selection/*.txt` | included | 3000 tool-selection queries (600 per class) | Appendix B proxy (mixed) |
| `data/processed/logging_ablation_extracted.json` | included | Static certificate ablation | Table 1 |
| `data/processed/proxy_ablation.json` | included | Resolution ablation results | Table 2 |
| `data/processed/proxy_dormant_active.json` | included | Dormant/active proxy split | Table 2 |
| `data/processed/intervention/*.json` | included | Intervention & replay results | Tables 3–4 |
| `data/processed/intervention/*_summary.csv` | included | ReAct intervention/replay summary tables | Tables 3–4 |
| `data/processed/intervention/raw/intervention_*_samples.jsonl` | generated | Per-sample ReAct intervention tool distributions | Table 3 audit |
| `data/processed/diffusion_certificate/llada_temporal_k10.json` | included | LLaDA temporal certificate profile (per-step JS divergence) | §6.3 |
| `data/processed/diffusion_certificate/llada_temporal_k10.csv` | included | LLaDA temporal summary table | §6.3 |
| `data/processed/multi_agent_certificate/summary.json` | included | Multi-agent private-report JS summary | §6.4 |
| `data/processed/multi_agent_certificate/summary.csv` | included | Multi-agent private-report summary table | §6.4 |
| `data/processed/multi_agent_certificate/reports.jsonl` | generated | Full worker reports | §6.4 |
| `data/processed/multi_agent_certificate/actions.jsonl` | generated | Full controller samples | §6.4 |
| `data/processed/probe_pairs.pt` | generated | $(\Phi_t, Z_t, A_t)$ tensor pairs | Appendix B CE-diff estimation |
| `data/processed/probe_meta.json` | generated | Probe metadata (labels, dims) | Appendix B |
| `data/processed/synthetic/` | generated | Synthetic ground-truth results | Appendix E |

Additional raw data files (`data/proxy_planning/`, `data/proxy_injected/`, `data/episodes/`) are not included; the precomputed results above cover Tables 1–4. The proxy planning/injected trajectories are regenerated on-the-fly by `run_proxy_dormant_active.py`.

Paper tables and headline macros are rendered from the checked-in processed
JSON/CSV files:

```bash
python3 experiments/render_paper_tables.py
```

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
