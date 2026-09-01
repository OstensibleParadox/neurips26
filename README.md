# Dual Certificates: Research Reset

This repository is in a **pre-gate research reset**. The active direction is
finite-sample, probe-relative certification of transcript insufficiency in
neural agents:

> Given a declared family of admissible interventions, is the public transcript
> sufficient to simulate every safety-relevant action distribution of the
> deployed agent?

The full research plan is in [`README_NEW_DIRECTION.md`](README_NEW_DIRECTION.md).
It is a go/no-go plan, not a statement of completed results. Gate status is
tracked in [`GO_NO_GO.md`](GO_NO_GO.md) and is **INCONCLUSIVE by default**.

## Current Decision

**INCONCLUSIVE — the go/no-go gate has not passed.**

Do not rewrite the full paper, tag the legacy release, promote `paper_v2/`, or
delete old experiments while this status remains `INCONCLUSIVE`.

## Repository Status Matrix

| Path | Status | Allowed work |
|---|---|---|
| `README_NEW_DIRECTION.md` | Current research specification | Keep aligned with the active audit contract and gate. |
| `GO_NO_GO.md` | Current decision record | Add evidence and record a decision without weakening preregistered thresholds. |
| `paper/` | **Legacy, read-only** | Preserve exactly as the abandoned latent-state/capacity-map paper record. |
| `paper_v2/` | Pre-gate incubator | Keep scaffolding and concise working notes only; no full-paper rewrite before GO. |
| `experiments/8.1_tracetwin/` | Active | Exact passive twins, controlled-clamp calibration, and passive-baseline tests. |
| `experiments/8.2_sequential_certificate/` | Active | Predictable decoder/e-process implementation, optional-stopping tests, and finite-sample calibration. |
| `experiments/8.3_agentdojo/` | Active | One real, consequential, trace-clamped structured-action boundary with strict controls. |
| `src/` | Shared and reusable | Extend shared trace, randomization, inference, and evaluation utilities while preserving compatibility. |
| `experiments/7.3_intervention/` | Reusable infrastructure | Reuse replay/intervention machinery and discrete-action evaluation; do not treat off-support ablations as primary evidence. |
| `experiments/7.4_synthetic_gt/` | **Ground-truth repair complete; historical validation quarantined** | The noise-consistent target and regression tests may be reused; withdrawn estimator outputs may not be cited or used as gate evidence until regenerated and reviewed. |
| `experiments/7.1_static_certificate/` | **Frozen legacy** | Reproduction only; no extension. |
| `experiments/7.2_dynamic_certificate/` | **Frozen legacy** | Reproduction only; no extension. |
| `experiments/7.5_diffusion_certificate/` | **Frozen legacy** | Reproduction only; no extension. |
| `experiments/7.6_multi_agent_certificate/` | **Frozen legacy** | Reproduction only; no extension. |
| `data/processed/` | Preserved artifacts | Retain artifacts needed to reproduce existing pilots; keep new gate evidence clearly separated. |

## Legacy Boundary

The immutable legacy baseline is Git commit:

```text
50cec93
```

This commit identifies the old latent-state/capacity-map version. No legacy tag
is created during the pre-gate phase. If and only if the gate reaches `GO`, the
tag `legacy-latent-state-certificates` must point to **exactly `50cec93`**, not
to the then-current branch tip.

`paper/` must not be edited, reformatted, rebuilt in place, cleaned, renamed, or
used as the destination for generated files. The root `Makefile` now routes
`make paper`, `make pdf`, and `make clean` exclusively to `paper_v2/`; every
paper build first runs `make check-legacy-paper` against the frozen tree.

The frozen experiment directories must likewise not receive code, config,
documentation, or generated-output changes. Their commands remain documented in
[`experiments/README.md`](experiments/README.md) solely for historical
reproduction.

## Active Workstreams

### 8.1 TraceTwin

Build two mechanisms with exactly the same passive distribution `P(T,A)`:

- a transcript-mediated visible twin; and
- a latent-bypass twin.

The workstream must verify passive equality, analytic values in both the
passive-label and controlled-clamp regimes, null false-positive control, power,
mixture monotonicity, confidence coverage, adaptive-probe validity, and failure
of passive trace-only classifiers.

### 8.2 Sequential Certificate

Implement the anytime-valid evidence process for adaptive probes. The probe
policy and normalized decoder must be predictable from the pre-round history,
the probe law must have full support, and the primary implementable protocol
must use a known denominator supplied by exact conditional trace clamping.

An estimated induced probe law is not an exact Ville-valid denominator unless a
separate robust guarantee is proved.

### 8.3 Real Structured-Action Boundary

Use natural, on-support paired private states and hold the public transcript,
model, prompt, and unrelated state fixed. Measure a real structured action such
as recipient, amount, approve/deny, tool endpoint, or write target—not only
token logits.

Primary evidence admits only exact or predeclared trace-equivalent pairs. Zero,
blank, Gaussian, and arbitrary-text ablations are cautionary baselines. Required
controls include active, visible-twin, dormant, disconnected, same-class
nuisance, full-logging oracle, transcript-only monitor, and marginal action-rate
conditions.

## Reuse Policy

Reuse existing code without reviving the old claim:

- `src/trace_schema.py` and `src/utils/` for shared records, seeding, bootstrap,
  randomization, and I/O;
- replay and intervention machinery from `experiments/7.3_intervention/`; and
- discrete action-level TV, JS, bounded advantage, cluster bootstrap, and
  randomization-inference components.

Gate-quality results must use discrete safety-relevant actions with task-block
bootstrap or randomization inference. A fragile neural mutual-information
estimator, logit-only effect, or failed finite classifier is not a certificate.

## Three-State Gate

The decision rule is intentionally strict:

- **GO**: every required GO criterion passes, no NO-GO condition is present,
  and TraceTwin, the sequential certificate, and one real trace-clamped action
  experiment all have reviewable evidence.
- **NO-GO**: any explicit NO-GO condition is observed. Stop the project rather
  than returning to the capacity-map narrative.
- **INCONCLUSIVE**: evidence is missing, a GO threshold is unmet without an
  explicit NO-GO finding, or the lower and upper certificates do not resolve.
  Continue only scoped gate work; do not promote the paper.

The exact thresholds, negative conditions, evidence paths, and decision record
are in [`GO_NO_GO.md`](GO_NO_GO.md).

## Actions Allowed Only After GO

After a documented `GO`, and not before:

1. Create `legacy-latent-state-certificates` at commit `50cec93`.
2. Promote `paper_v2/` to the formal `paper/` only after the legacy source is
   recoverable from that tag.
3. Delete from the main branch only legacy experiments that the new paper no
   longer depends on; the tag must remain the recovery point.

These are post-gate migration actions, not part of the current scaffold.

## Claim Boundary

The project may certify only claims relative to a declared deployment
distribution, access model, logging boundary, admissible probe family, and
safety-relevant action boundary. It must not claim full latent-state recovery,
absence of every hidden channel, universal transcript faithfulness, mechanism
identification from Markov equivalence, or decoder-independent
non-recoverability from one monitor's failure.

## Repository Boundary

This repository contains only the Dual Certificates paper, experiments, and
artifacts. The Lean/formal proof artifact (`CausalQIF`) and the
infinitesimal-Shannon/operator-theory manuscript (`infinitesimal-shannon`) are
separate projects and must not be merged here.
