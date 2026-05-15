# AuditBench Scale-Up Plan

Goal: turn the current dual-certificate proof of concept into a systematic
measurement benchmark for agent audit. The target claim is not that scale
guarantees an oral. The target claim is:

> Hidden capacity and behavioral activation systematically decouple across
> model scale, task family, and agent topology.

The scaled paper should become:

> We introduce AuditBench, a benchmark for measuring the gap between hidden
> capacity and behavioral activation in language-model agents. Across models,
> tasks, and communication topologies, structural hidden capacity can remain
> fixed while behavioral activation varies by orders of magnitude.

## 0. Main Principle

Do not spend cluster time only making existing numbers larger. Spend cluster
time producing laws:

- Scaling law: how `delta_act_LB` changes with model size and task difficulty.
- Topology law: how communication structure changes activation.
- Activation law: where hidden state becomes action-relevant.
- Outcome law: when soft policy shifts become realized action flips or task
  failures.

Every experiment must report both information-flow metrics and decision-level
metrics. Reviewers already objected that soft JS/MI shifts alone do not prove
decision relevance.

## 1. ReAct Main Matrix

This is the highest-priority experiment. It directly tests the main paper claim:
same scratchpad topology, fixed static capacity, different behavioral activation.

### Axes

- Models: 6-8 models if possible.
  - 7B/8B class.
  - 13B/14B class.
  - 30B/32B class.
  - 70B class if the cluster supports it.
- Task families: at least 6.
  - calculator.
  - simple tool routing.
  - multi-hop planning.
  - memory lookup.
  - retrieval QA.
  - long-horizon tool use.
  - optional safety-sensitive routing.
- Logging regimes:
  - output only.
  - `+router`.
  - `+scratchpad`.
  - full instrumentation.
- Probe types:
  - replay.
  - mask.
  - replace.
  - proxy.
  - negative controls.
- Seeds: at least 5.

### Scale

- Minimum: 100k ReAct episodes.
- Stronger target: 200k ReAct episodes.
- Prompt count per task family: 1,000-3,000 before seeds/probes.

### Metrics Per Cell

- `epsilon_state_UB`.
- `delta_act_LB`.
- JS divergence in bits.
- CE gap.
- `argmax_action_flip_rate`.
- `task_success`.
- `success_delta`.
- `wrong_tool_rate`.
- `unsafe_action_rate`, when applicable.
- 95% task-block bootstrap confidence interval.

### Required Controls

- Null replay.
- Random hidden channel.
- Wrong module intervention.
- Same visible trace, shuffled hidden state.
- Perturbation sweep for mask/replace interventions.

### Core Figure

Main heatmap:

```text
(model_size) x (task_family) x (probe_type)
```

Each cell should show `delta_act_LB` and optionally annotate action flip rate.

Secondary figures:

- `delta_act_LB` vs planning depth.
- action flip rate vs perturbation strength.
- `epsilon_state_UB` vs logging regime.
- hidden activation vs model scale.

## 2. Multi-Agent Topology Suite

This is the second-highest priority because the effect size is currently strong
and can become a topology law.

### Topologies

- `1_worker_to_controller`: baseline.
- `3_workers_majority_vote`: hidden influence should distribute across peers.
- `specialist_workers`: evidence-routing topology.
- `adversarial_worker`: untrusted channel saturation.
- `memory_augmented_worker`: compare report edge vs memory edge.
- `debate_agents`: test whether min-cut predicts activation points.
- optional `hierarchical_controller`: coordinator/subcontroller split.

### Task Families

- arithmetic.
- multi-hop QA.
- code/tool choice.
- retrieval-required QA.
- planning.
- ambiguous routing.

### Scale

- Minimum: 5 topologies.
- Stronger target: 8 topologies.
- Minimum: 50k multi-agent sample units.
- Stronger target: 100k sample units.
- Controller samples per item: `k=16` minimum, `k=32` preferred.

### Metrics

- `epsilon_state_UB` by topology.
- `delta_act_LB` by communication edge.
- JS bits and CI.
- action flip rate under report swap.
- task success delta.
- wrong-tool rate.
- edge-level activation profile.

### Required Controls

- Neutral replay.
- Same-class shuffle.
- Opposite-class report.
- Random report.
- Report leakage audit.
- Adversarial worker with and without trust reclassification.

### Core Figure

Topology plot:

```text
min-cut capacity -> predicted active edge -> observed delta_act_LB
```

The desired result is not merely "reports matter." The desired result is that
activation changes systematically with communication topology.

## 3. Diffusion-LM / LLaDA Temporal Study

This is the third priority. It has the most novelty as a non-autoregressive
agent geometry, but it is computationally expensive and more fragile.

### Axes

- Diffusion models: 2-3 if available.
- Denoising schedules: `K=10,32,64,128`.
- Probed steps: 8-16 steps per schedule.
- Layers:
  - early.
  - middle.
  - late.
  - final.
- Perturbation strengths:
  - small.
  - medium.
  - large.
  - extreme.
- Controls:
  - null perturbation.
  - random layer.
  - visible-trace perturbation.
  - wrong-step perturbation.

### Scale

- Minimum: 20k trajectories.
- Stronger target: 50k trajectories.
- Minimum per `(step, layer, sigma)` cell: 500 trajectories when feasible.

### Metrics

- temporal `delta_act_LB`.
- action flip rate.
- task success delta.
- off-manifold score.
- perturbation dose-response.
- target-layer vs control-layer gap.

### Core Finding To Test

> Decision relevance concentrates near action binding across denoising schedules.

If the controls also rise at final steps, state the narrower result:

> Denoising models exhibit broad final-step action sensitivity, with localized
> hidden-channel activation only when target-layer effects exceed controls.

## 4. AuditBench Release

AuditBench should be a benchmark artifact, not only a pile of experiment logs.

### Contents

1. Standard agent topologies.
2. Standard logging manifests.
3. Standard hidden-channel interventions.
4. Standard task families.
5. Standard estimators:
   - JS divergence.
   - CE gap.
   - bootstrap CI.
   - static min-cut capacity.
6. Standard outputs:
   - `(epsilon_state_UB, delta_act_LB)`.
   - action flip rate.
   - task outcome deltas.
   - negative-control diagnostics.

### Proposed Directory

```text
experiments/auditbench/
├── configs/
│   ├── models.yaml
│   ├── tasks.yaml
│   ├── topologies.yaml
│   ├── logging_regimes.yaml
│   └── probes.yaml
├── runners/
│   ├── run_react.py
│   ├── run_diffusion.py
│   └── run_multiagent.py
├── certificates/
│   ├── static_mincut.py
│   ├── dynamic_js.py
│   ├── proxy_ce_gap.py
│   └── bootstrap.py
├── outputs/
│   ├── raw_traces/
│   ├── action_probs/
│   ├── interventions/
│   ├── certificates/
│   └── figures/
└── schemas/
    ├── run_record.schema.json
    └── certificate_record.schema.json
```

## 5. Infra Task Specification

The cluster runner should be resumable, hash-addressed, and embarrassingly
parallel. Infra does not need to understand the paper. It only needs to execute
the matrix and write structured records.

### Run Key

```text
run_id = hash(
  model,
  task_family,
  task_id,
  topology,
  logging_regime,
  probe_type,
  condition,
  seed,
  perturbation_sigma,
  decoding_policy
)
```

### Required Input Fields

- `model`.
- `model_size`.
- `task_family`.
- `task_id`.
- `topology`.
- `logging_regime`.
- `probe_type`.
- `condition`.
- `seed`.
- `perturbation_sigma`.
- `sampling_temperature`.
- `decoding_policy`.

### Required Output Fields

- `run_id`.
- `model`.
- `model_size`.
- `topology`.
- `task_family`.
- `task_id`.
- `seed`.
- `logging_regime`.
- `probe_type`.
- `condition`.
- `visible_trace_hash`.
- `hidden_channel_id`.
- `intervention_payload_hash`.
- `action_distribution`.
- `argmax_action`.
- `realized_action`.
- `tool_token_probs`.
- `action_flip_under_probe`.
- `task_success`.
- `success_delta`.
- `wrong_tool`.
- `unsafe_action`.
- `trajectory_return`.
- `probe_validity_control`.
- `off_manifold_score`.
- `epsilon_state_UB`.
- `delta_act_LB`.
- `bootstrap_CI_low`.
- `bootstrap_CI_high`.

### Storage Format

- Raw per-run records: JSONL.
- Aggregated tables: Parquet.
- Configs: YAML.
- Figure inputs: CSV or Parquet.
- Metadata: one `metadata.yaml` per batch.

Do not rely on stdout as the experiment artifact.

## 6. Compute Priority

1. ReAct matrix.
   - Reason: direct test of the core claim.
   - Target: 100k-200k episodes.
2. Multi-agent topology suite.
   - Reason: strongest current effect and best topology-law opportunity.
   - Target: 50k-100k sample units.
3. Diffusion temporal study.
   - Reason: high novelty but high risk/cost.
   - Target: 20k-50k trajectories.

If compute becomes constrained, protect breadth across models/tasks/topologies
before spending heavily on one very large model.

## 7. Oral-Shot Acceptance Bar

These are internal acceptance bars for the scale-up, not guarantees of oral.

| Module | Minimum |
| --- | ---: |
| ReAct models | 6 |
| ReAct task families | 6 |
| ReAct episodes | 100k |
| Multi-agent topologies | 5 |
| Multi-agent sample units | 50k |
| Diffusion trajectories | 20k |
| Seeds | 5 |
| Controls | every probe has a negative control |
| Metrics | JS + CE gap + flip rate + task outcome |
| Release | code + configs + cached traces + AuditBench schemas |

The stronger bar is:

| Module | Strong Target |
| --- | ---: |
| ReAct episodes | 200k |
| Multi-agent sample units | 100k |
| Diffusion trajectories | 50k |
| Multi-agent topologies | 8 |
| Models | 8 |

## 8. Paper Narrative After Scale-Up

Avoid this framing:

> We propose dual certificates and test them on three examples.

Use this framing:

> We introduce AuditBench, a systematic benchmark for agent observability. It
> measures the gap between structural hidden capacity and behavioral activation
> across models, tasks, and topologies. The core empirical finding is stable
> decoupling: capacity can remain fixed while activation changes by task,
> topology, and action-binding stage.

The deciding evidence should be:

- controls stay flat;
- true hidden channels rise;
- outcome metrics move when activation is high;
- static capacity alone does not predict behavioral use;
- topology and task family explain activation better than raw hidden capacity.

