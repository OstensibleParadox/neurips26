# Two-Week Go/No-Go Gate

This file is the decision record for the research reset defined in
[`README_NEW_DIRECTION.md`](README_NEW_DIRECTION.md). It records evidence; it
does not turn planned experiments into completed results.

## Current Decision

| Field | Value |
|---|---|
| Status | **INCONCLUSIVE** |
| Evaluated at | Not yet evaluated |
| Evidence commit | Not yet recorded |
| Decision owner/reviewer | Not yet recorded |
| Legacy baseline | `50cec93` |
| Legacy tag | Not created; forbidden before GO |

`INCONCLUSIVE` is the default and remains in force until the evidence below is
complete and reviewed.

## Decision Semantics

- **GO** requires every gate prerequisite and every GO criterion to be `PASS`,
  with every NO-GO condition marked `ABSENT`.
- **NO-GO** is required as soon as any NO-GO condition is supported by the
  evidence. The project stops; it does not return to the old capacity-map
  narrative.
- **INCONCLUSIVE** applies whenever evidence is missing, a GO threshold is not
  met without establishing a listed NO-GO condition, or the lower and upper
  certificates leave an unresolved gap.

A missing file, failed run, point estimate without its required uncertainty, or
unreviewed result is not a pass.

## Evidence Contract

Gate evidence must:

- record the producing Git commit, command/config, random seeds, sample counts,
  model or suite identifiers, and action schema;
- use auditor-randomized, admissible, on-support probes at a declared boundary;
- measure real discrete structured actions rather than relying on token logits;
- report task-block bootstrap or randomization-inference uncertainty;
- verify exact byte/schema trace equality or a predeclared trace-equivalence
  test, including arm-leakage diagnostics;
- separate passive-label and controlled-clamp TraceTwin regimes;
- keep active, visible-twin, dormant, disconnected, same-class, full-logging,
  off-support, transcript-monitor, and marginal-rate controls distinguishable;
  and
- preserve raw observations or a reproducible manifest sufficient to recompute
  every gate statistic.

The paths below are the canonical evidence destinations. If an implementation
uses a different filename, update this document before evaluating the gate and
link the exact replacement. Do not mark a row `PASS`, `ABSENT`, or `PRESENT`
without an existing reviewable artifact.

## Gate Prerequisites

| ID | Requirement | Required evidence | Canonical evidence path | Status |
|---|---|---|---|---|
| P1 | TraceTwin calibration is complete. | Passive `P(T,A)` equality, analytic agreement in passive-label and controlled-clamp regimes, coverage, mixture monotonicity, and passive-baseline results. | `data/processed/8.1_tracetwin/gate_summary.json` | PENDING |
| P2 | Sequential certificate is valid under adaptive probes and optional stopping. | Null crossing rates, stopping-time runs, predictable decoder/probe audit, full-support check, and exact-clamp denominator check. | `data/processed/8.2_sequential_certificate/gate_summary.json` | PENDING |
| P3 | One realistic trace-clamped structured-action experiment is complete. | 50–100 paired private-state cases, 8–16 stochastic repetitions per arm where feasible, actual action outcomes, and all required controls. | `data/processed/8.3_agentdojo/gate_summary.json` | PENDING |
| P4 | Replication design is complete. | At least two open-weight tool-use models or two task suites under the same declared audit contract. | `data/processed/8.3_agentdojo/replication.json` | PENDING |

## GO Criteria

Every row must be `PASS` for a GO decision.

| ID | Prespecified criterion | Evidence to record | Canonical evidence path | Status |
|---|---|---|---|---|
| G1 | Null false-positive rate is at or below the nominal `5%` level. | Number of null trials, rejection rule, observed rate, confidence interval, and optional-stopping/adaptive results. | `data/processed/8.1_tracetwin/null_calibration.json`; `data/processed/8.2_sequential_certificate/null_calibration.json` | PENDING |
| G2 | Power is at least `80%` for a prespecified meaningful action effect. | Effect definition fixed before evaluation, simulation or paired-case design, observed power, and uncertainty. | `data/processed/8.1_tracetwin/power.json`; `data/processed/8.3_agentdojo/power.json` | PENDING |
| G3 | Passive TraceTwin classifier AUC is at most `0.55`. | Held-out, passive-only classifier protocol, AUC, interval, and proof that randomized probe labels were unavailable. | `data/processed/8.1_tracetwin/passive_baselines.json` | PENDING |
| G4 | Structured-trace equivalence is at least `95%`, preferably exact by design. | Pair-level byte/schema hashes, equivalence decision, mismatch reasons, and arm-leakage diagnostic. | `data/processed/8.3_agentdojo/trace_equivalence.json` | PENDING |
| G5 | The realistic active condition has a positive action-effect lower certificate. | Discrete action statistic, lower confidence bound strictly above zero, probe family, and declared transcript/action boundaries. | `data/processed/8.3_agentdojo/action_certificate.json` | PENDING |
| G6 | Dormant, disconnected, same-class, and visible-twin controls are null. | Per-control estimates, intervals/tests, multiplicity rule if used, and prespecified null acceptance region. | `data/processed/8.3_agentdojo/controls.json` | PENDING |
| G7 | The result replicates across at least two models or two suites. | Per-replicate estimates and certificates under matched protocol, plus pooled and heterogeneity summaries. | `data/processed/8.3_agentdojo/replication.json` | PENDING |

## NO-GO Conditions

Any row marked `PRESENT` forces a NO-GO decision. Missing evidence leaves the
gate `INCONCLUSIVE`; it does not establish `ABSENT`.

| ID | Stop condition | Evidence to inspect | Canonical evidence path | Status |
|---|---|---|---|---|
| N1 | Effects appear only under zero, blank, Gaussian, or arbitrary-text ablations. | Side-by-side on-support and off-support effect estimates. | `data/processed/8.3_agentdojo/ablation_comparison.json` | UNKNOWN |
| N2 | Natural on-support private-state swaps do not change real actions. | Active-condition action distributions and lower certificate. | `data/processed/8.3_agentdojo/action_certificate.json` | UNKNOWN |
| N3 | The transcript reliably reveals the randomized probe arm. | Predeclared arm-leakage test, classifier performance, and pair-level trace mismatches. | `data/processed/8.3_agentdojo/trace_equivalence.json` | UNKNOWN |
| N4 | The result requires logits or an unstable neural MI estimator. | Measurement/estimator manifest showing whether the conclusion survives using structured actions and finite-sample discrete inference alone. | `data/processed/8.3_agentdojo/estimator_audit.json` | UNKNOWN |
| N5 | Passive methods distinguish the supposedly observationally identical TraceTwin mechanisms. | Passive held-out baselines and numerical `P(T,A)` equality checks. | `data/processed/8.1_tracetwin/passive_baselines.json` | UNKNOWN |
| N6 | No useful upper certificate is obtained beyond raw embedding-width capacity. | Transcript-only simulator upper certificate and comparison with the legacy width envelope. | `data/processed/8.2_sequential_certificate/simulator_upper_certificate.json` | UNKNOWN |
| N7 | The empirical result reduces to a controller following a private report that explicitly contains the action label. | Protocol audit of every private field, report template, and action mapping. | `data/processed/8.3_agentdojo/protocol_audit.json` | UNKNOWN |

## Workstream-Specific Review Checks

### TraceTwin

- [ ] The mediated and bypass mechanisms have numerically equal passive
  `P(T,A)` within the declared numerical tolerance.
- [ ] Passive-label information is checked against `h2(r) - h2(rho)`.
- [ ] Controlled-clamp information is checked separately against
  `1 - h2(rho)`.
- [ ] The two regimes are never pooled or reported as the same estimand.
- [ ] False-positive control, power, confidence coverage, mixture monotonicity,
  adaptive probes, and passive baselines are all reported.

### Sequential Certificate

- [ ] Each probe policy has full support and is measurable with respect to the
  pre-round history.
- [ ] The complete normalized decoder rule is fixed before the current probe
  label is revealed.
- [ ] The denominator is the known randomization law under exact conditional
  trace clamping.
- [ ] No plug-in estimate of an unknown induced probe law is presented as an
  exact Ville-valid e-factor.
- [ ] Type-I error is calibrated under fixed horizons, optional stopping, and
  adaptive probe policies.

### Real Action Boundary

- [ ] Private-state pairs are natural, on support, and differ in one declared
  security-relevant field.
- [ ] Public task, public transcript, model, prompt, and unrelated state are
  held fixed or matched under a predeclared equivalence rule.
- [ ] The execution sink is a structured consequential action.
- [ ] Only exact or predeclared trace-equivalent pairs enter the primary
  certificate.
- [ ] All negative controls and the full-logging oracle are reported.
- [ ] Inference resamples or randomizes at the paired task/case level.

## Decision Record

Complete this section only after reviewing all artifacts.

| Field | Entry |
|---|---|
| Final state (`GO`, `NO-GO`, or `INCONCLUSIVE`) | INCONCLUSIVE |
| Evidence commit | — |
| Reviewed artifact manifest | — |
| Failed or unresolved criterion IDs | P1–P4, G1–G7; N1–N7 unknown |
| Decision rationale | Gate evidence has not yet been produced. |
| Reviewer and date | — |

Changing the state requires updating the criterion tables and citing the exact
evidence commit. Thresholds must not be relaxed after inspecting results; a
changed scientific target requires a new preregistered gate rather than editing
this one retroactively.

## Post-GO Migration Checklist

This checklist is locked while the decision is `INCONCLUSIVE` or `NO-GO`.

- [ ] Confirm the final decision is `GO` at a recorded evidence commit.
- [ ] Create `legacy-latent-state-certificates` pointing to commit `50cec93`.
- [ ] Verify the tag resolves to the same commit as `50cec93`; never tag the
  current post-reset branch tip by accident.
- [ ] Promote `paper_v2/` to `paper/` only after the tag is verified.
- [ ] Identify dependencies of the new paper before removing legacy
  experiments from the main branch.
- [ ] Verify every removed legacy artifact remains recoverable from the tag.

The expected tag operation, to be run only after GO, is conceptually:

```bash
git tag legacy-latent-state-certificates 50cec93
```

Both of these resolutions must then identify the same commit:

```bash
git rev-parse legacy-latent-state-certificates^{commit}
git rev-parse 50cec93^{commit}
```
