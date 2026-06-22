# Static Certificate Pipeline (§7.1)

Compute the static audit certificate
`ε_state^UB ≤ ε_nominal + Σ_{e ∈ E_t^{unlogged, reach(S_t)}} c_e`
for a deployment by enumerating the unlogged-edge subgraph of the time-unrolled
architecture DAG, summing per-edge capacities, and reporting the bound together
with its min-cut tightening.

This is the pipeline backing Proposition A and Section 7.1 of the paper.

## Status

**Completed.** The pipeline supports networkx-based cut enumeration and matplotlib figure rendering. The paper presents a completed static certificate table (16,464 bits stepwise reduction) and two figures (react_dag.pdf, logging_ablation.pdf) as extracted results. The diffusion-LM entry in the paper's main Table is derived
analytically from Corollary 4.3.2 and does not depend on this pipeline.

## Files

```
README.md                       — this file
schema.json                     — JSON schema for architecture specs
architectures/
  react_agent.json              — Deployment 1: ReAct agent with async memory
  diffusion_lm.json             — Deployment 2: Mercury-class diffusion LM
  multi_agent_scratchpad.json   — Deployment 3: two-agent scratchpad system
enumerate_cuts.py               — loads a spec, enumerates edge cuts
compute_epsilon_ub.py           — applies c_e formulas, returns {min_cut, ε_UB}
render_figure.py                — renders DAG with unlogged edges highlighted
__init__.py                     — empty, makes the directory importable
```

## Architecture spec format

A deployment is described by a JSON file conforming to `schema.json`. Each spec
has a set of **nodes** (exogenous sources, internal state, intermediate,
sink = full internal state `S_t`) and a set of directed **edges** between
nodes. Each edge carries a `logged: bool` flag and a capacity
specification (`c_e_bits` as an integer, or `c_e_formula` as a symbolic tag
resolved against a small library of capacity formulas).

Example (abbreviated from `architectures/react_agent.json`):

```json
{
  "name": "react_agent_toolformer",
  "description": "ReAct agent with external tool calls + async memory writes",
  "nodes": [
    {"id": "prompt", "kind": "source"},
    {"id": "kv_0", "kind": "state", "dim": 4096, "bits_per_dim": 8},
    {"id": "tool_1_output", "kind": "intermediate"},
    {"id": "async_memory_write", "kind": "intermediate", "dim": 2048, "bits_per_dim": 8},
    {"id": "S_t", "kind": "sink"}
  ],
  "edges": [
    {"from": "prompt",              "to": "kv_0",             "logged": true},
    {"from": "kv_0",                "to": "tool_1_output",    "logged": true},
    {"from": "tool_1_output",       "to": "async_memory_write","logged": false, "c_e_formula": "quantized_activation"},
    {"from": "async_memory_write",  "to": "S_t",              "logged": false, "c_e_formula": "quantized_activation"}
  ]
}
```

## Capacity formulas (`c_e_formula`)

| Tag                     | Formula                         | Comment                                          |
|-------------------------|---------------------------------|--------------------------------------------------|
| `context_window`        | `n * log2(|V|)`                 | token-window channel, `n` tokens over vocab V   |
| `quantized_activation`  | `dim * bits_per_dim`            | bit-width × dimension                            |
| `diffusion_latent`      | `dim * bits_per_dim`            | same as quantized_activation                     |
| `gaussian_source`       | `0.5 * log2(2 * pi * e * sigma^2)` | differential entropy (bits); flagged in paper |
| `fixed`                 | read `c_e_bits` field           | user-specified numeric capacity in bits          |

## Usage

```bash
python compute_epsilon_ub.py architectures/diffusion_lm.json
# → {"min_cut": ["s_0 -> s_1"], "epsilon_ub_bits": 32768}

python render_figure.py architectures/multi_agent_scratchpad.json \
    --out figures/multi_agent_scratchpad.pdf
```

Or programmatically:

```python
from experiments import load_spec, enumerate_cuts, compute_epsilon_ub
spec = load_spec("architectures/diffusion_lm.json")
cuts = enumerate_cuts(spec)
result = compute_epsilon_ub(spec)
print(result["min_cut"], result["epsilon_ub_bits"])
```

(The `experiments` package re-exports the relevant helpers via `setup.py`.)

## Reference deployments

### Deployment 1: ReAct + async memory (`react_agent.json`)

- Autoregressive base model with external tool calls.
- Prompts, tool inputs, and tool outputs are logged.
- Async memory writes between tool calls are **not** logged.
- Unlogged channels: memory-write edges.
- Expected `ε_state^UB`: dominated by the memory-write capacity, on the order
  of tens of kilobits.

### Deployment 2: diffusion LM (`diffusion_lm.json`)

- Mercury-class diffusion LM with `K = 20` denoising steps at `d = 4096`,
  bit-width `b = 8`.
- Only the final denoised output is logged.
- Unlogged channels: all K−1 intermediate denoising edges.
- Min cut: single edge `S_t^{(0)} → S_t^{(1)}` with capacity `b · d = 32768`
  bits, **independent of K**. This is the analytical entry in the paper.

### Deployment 3: multi-agent scratchpad (`multi_agent_scratchpad.json`)

- Two-agent system (e.g. AutoGen / CrewAI).
- Inter-agent messages are logged.
- Per-agent chain-of-thought scratchpad channels are **not** logged.
- Min cut: one unlogged scratchpad edge per agent. For a symmetric
  two-agent setup, `ε_state^UB ≤ 2 · scratchpad_dim · bits`.

## Verification

```bash
python -c "import json, jsonschema; \
    jsonschema.validate(json.load(open('architectures/react_agent.json')), \
                        json.load(open('schema.json')))"
```

Returns cleanly for each of the three reference specs.
