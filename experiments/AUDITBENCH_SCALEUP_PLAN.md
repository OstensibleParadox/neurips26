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
│   └── ... (YAML configs)
├── runners/
│   ├── run_react.py
│   ├── run_diffusion.py
│   └── run_multiagent.py
├── submit/
│   ├── generate_manifest.py
│   └── submit_rjob.sh
├── aggregate/
│   ├── calculate_ci.py
│   └── plot_heatmaps.py
├── outputs/
│   ├── figures/
│   └── ... (JSONL outputs)
└── schemas/
    └── run_record.py
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

## 9. 算力规格（供 infra 调度用） / Compute Specification

### 9.1 job 定义 / Job Definition

不可再分的最小执行单元。One independent unit of work:

```
job_id = hash(model, model_size, task_family, task_id, topology,
              logging_regime, probe, condition, seed, sigma, temperature)
```

每个 job 产出一条 JSONL 记录。job 之间无共享状态。失败 job 按 hash 重放即可。
Each job produces one JSONL record. Jobs share no state. Failed jobs are retried by re-running the hash.

### 9.2 单 job 资源画像 / Per-Job Resource Profile

| 模型档位 Model Class | GPU | 最低显存 VRAM Floor | token/episode | 秒/episode | 可并行性 |
|---|---|---|---|---|---|
| 7B/8B（Qwen2.5, LLaMA） | A100-40G / A10 | 16 GB | ~1,500 | ~20s | 同节点多卡 |
| 14B（Qwen2.5-14B） | A100-40G | 28 GB | ~1,500 | ~35s | 同节点多卡 |
| 32B（Qwen2.5-32B） | A100-80G | 40 GB | ~1,500 | ~70s | 单卡 1-2 个 |
| 70B+（Qwen2.5-72B） | A100-80G | ≥70 GB | ~1,500 | ~120s | 单卡 1 个，可能需张量并行 |

多 agent controller 调用极短：每次约 100 token 输出，~5s，每个 item 调 k=16-32 次。
LLaDA 扩散模型单次前向约为同尺寸自回归模型的 2-3 倍慢（每步双向去噪 × K 步退火）。

Multi-agent controller calls: ~100 tokens output each, ~5s per call, k=16-32 per item.
LLaDA diffusion: ~2-3× slower than same-size autoregressive (bidirectional denoising × K steps).

<!-- TODO: reconcile compute spec arithmetic — ReAct totals do not sum to the stated 320k and diffusion cell count is ~2× the stated trajectory count -->

### 9.3 job 总数与 GPU 小时预算 / Job Count and GPU-Hour Budget

#### ReAct 主矩阵 / ReAct Main Matrix（minimum: 100k episode）

| 乘项 | 数量 |
|---|---|
| 模型 models | 6（2×7B, 1×14B, 1×32B, 1×70B, 1×备用） |
| 任务族 task families | 6 |
| seed | 5 |
| logging regime | 4 |
| 人均 probe 数 | ≈3.5 |
| 每 (模型, 任务族, seed) prompt 数 | 150 |
| **推理调用总数 total inference calls** | **≈320,000** |
| **GPU 小时总计 total GPU-hours（A100-equiv）** | **≈3,000–3,500** |

按模型规模拆分 / By model scale:

| 规模 | 推理调用 | 秒/次 | GPU 小时 |
|---|---|---|---|
| 7B/8B × 2 | ≈110,000 | 20 | ≈600 |
| 14B × 1 | ≈55,000 | 35 | ≈530 |
| 32B × 1 | ≈35,000 | 70 | ≈680 |
| 70B × 1 | ≈20,000 | 120 | ≈670 |

#### 多 agent 拓扑套件 / Multi-Agent Topology（minimum: 50k unit）

| 乘项 | 数量 |
|---|---|
| 拓扑 topologies | 5 |
| 任务族（均衡） | 4 |
| 每 (拓扑, 任务族) item 数 | 2,500 |
| 每 item controller 调用 (k) | 16 |
| 条件数（base + 3 probe） | 4 |
| **推理调用总数** | **≈800,000** |
| **GPU 小时总计** | **≈1,000–1,200** |

controller 调用短且便宜（7B/14B 上 ~5s/次）。

#### 扩散 / LLaDA 时间剖面 / Diffusion Temporal（minimum: 20k trajectory）

| 乘项 | 数量 |
|---|---|
| 模型 | 2（LLaDA-8B + 1 个若有） |
| 退火步数 K | 3（10, 32, 64） |
| 每 schedule 探测步数 | 8 |
| 探测层数 | 3（early, mid, late） |
| sigma | 3 |
| 每 cell trajectory | 500 |
| **推理调用总数** | **≈110,000** |
| 时长倍数（K 步 + 双向） | ≈自回归 3× |
| **GPU 小时总计** | **≈1,500–1,800** |

### 9.4 总计 / Total Budget

| 模块 | GPU 小时 (minimum) | GPU 小时 (strong) |
|---|---|---|
| ReAct 矩阵 | 3,000–3,500 | 6,000–7,000 |
| 多 agent 拓扑 | 1,000–1,200 | 2,000–2,500 |
| 扩散时间剖面 | 1,500–1,800 | 3,500–4,500 |
| **合计** | **≈5,500–6,500** | **≈12,000–14,000** |

集群换算 / In cluster terms:
- **Minimum:** 8×A100 节点约 **28–34 天**，或 4×A100 约 55–70 天。
- **Strong:** 8×A100 节点约 **60–75 天**，或 16×A100 约 30–40 天。

### 9.5 并行度 / Parallelism

所有位于同一 (model, topology) 组内的 job 是完全并行无依赖的——无 job 间通信、无共享状态、无执行顺序约束。集群有 N 张 GPU 时可同时跑 N 个独立 job，上限仅受单 job 显存约束。唯一顺序依赖性：一个模块的全部 cell 跑完后，再做聚合（bootstrap CI、热力图）。聚合是离线 CPU 任务，不占 GPU。

All jobs within a (model, topology) group are embarrassingly parallel — no inter-job communication, no shared state, no ordering constraints. N GPUs can run N independent jobs concurrently, limited only by VRAM per job. The only scheduling constraint: aggregation (bootstrap CIs, heatmap generation) runs after all cells for a module complete. This is a post-hoc CPU job, not on the GPU cluster.

### 9.6 算力受限时的砍法 / Priority Triage

1. **先砍扩散模组。** 风险最高、当前效应量最弱、可用模型最少。
2. 多 agent 拓扑从 5 种砍到 3 种（保留 1-worker、3-worker majority、adversarial）。
3. ReAct 模型从 6 个砍到 4 个（砍掉一个 7B，保留 7B / 14B / 32B / 70B 各一）。
4. ReAct seed 从 5 个砍到 3 个。
5. **绝对不砍：** 至少一个 70B 级模型、至少 6 个任务族、每个 probe 至少一个负对照、每个 cell 至少一个 outcome 指标。

---

## 10. 集群使用规范 / Cluster Ops Compliance

### 背景 / Context

近期集群运维发现存在 GPUburn 类脚本占用 worker 不关闭、交互式调试 session 长占不释放等问题，导致 16 卡任务完全无法排上，集群碎片化严重。部门将统一集群使用管理规范，带战略解码标签的重大任务有单独保障方案。各团队须自查高占用任务是否为真实计算任务。

Cluster ops recently flagged GPUburn-style scripts holding workers indefinitely, interactive debug sessions not released, and scheduling fragmentation blocking 16-GPU jobs. Department-wide cluster usage policy is forthcoming. Major tasks tagged with strategic-decode labels will receive dedicated resource guarantees.

### 本任务承诺 / AuditBench Commitments

**1. 只用 rjob 提交。** 本计划全部推理调用通过 `rjob` 提交为独立 job（9.1 节的 hash key 粒度）。每个 job 跑完即退出，不持有 worker。不允许任何交互式调试 session 长时间占用 GPU。

**All inference submitted via `rjob`.** Every job (hash-key granularity from §9.1) runs to completion and exits. No interactive debug sessions holding GPUs.

**2. 无 GPUburn / 无虚假占用。** 不在集群上运行 GPUburn 或任何空转脚本"占坑"。本任务是真实计算任务：每个 job 产生一条带完整输出字段的 JSONL 记录（§5 节），有可验证的产出。高占用 = 高利用 = 高产出。

**No GPUburn / no fake occupancy.** Every job produces a verifiable JSONL output record with all fields from §5. High occupancy means high utilization means high output.

**3. 运行后即释放。** 每个 job 是独立进程，运行完毕自动退出。不保留常驻 worker，不持有长连接。9.5 节已明确：job 之间无依赖、无通信、无共享状态。单个 job walltime 最长约 120s（70B），不存在"跑了好几天才发现挂掉"的情况。

**Release immediately after completion.** Each job is an independent process that exits on completion. No persistent workers, no long-held connections. No dependencies between jobs (§9.5). Max per-job walltime is ~120s (70B), so there is no "ran for days before anyone noticed it crashed" scenario.

**4. 可中断可重放。** 任何 job 失败或被杀，按 hash key 重放即可，不丢进度。计划可以在集群负载高时主动降速（减并发），不需要抢资源。

**Interruptible and replayable.** Failed/killed jobs are retried by re-running the hash. The run can be throttled during high cluster load — no need to fight for resources.

**5. 不做碎片化。** 因为所有 job 是独立、短生命周期、单 GPU 的（9.2 节），不会出现"一个 job 占了 7 张卡而实际只用 1 张"的碎片化场景。16 卡连续资源留给需要的人。

**No fragmentation.** All jobs are independent, short-lived, single-GPU (§9.2). No "one job holds 7 GPUs while actually using 1" scenario. Contiguous 16-GPU blocks stay available for tasks that need them.

### 团队自查条目 / Team Self-Check

- [ ] 本分区不存在 GPUburn 或类似空转脚本
- [ ] 本分区不存在交互式调试 session 长占 worker
- [ ] 所有高占用 job 均为实际推理任务，有 JSONL 产出可查
- [ ] 运行策略使用 rjob，不用 worker 直接跑
- [ ] 本计划可在 30 天内跑完 minimum bar，不形成长期资源占用

