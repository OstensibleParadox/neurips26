# 8.3 AgentDojo Action-Boundary Audit

Status: **protocol and descriptive/null-test evaluator ready; G5 lower-bound
method and real runs pending**.

No AgentDojo result is claimed in this repository yet.  This directory defines
the handoff between an AgentDojo-style runner and the v2 certificate pipeline.
It reuses the replay/intervention pattern from `../7.3_intervention/`, while
replacing off-support hidden-state noise and token-logit endpoints with:

- natural, on-support paired private records;
- a declared action-binding boundary;
- exact or predeclared structured-trace equivalence;
- real structured actions (recipient, amount, approve/deny, endpoint, target);
- task-level uncertainty and within-task arm-label randomization.

## Record contract

Write one JSON object per stochastic repetition using
[`case_schema.json`](case_schema.json).  Every case must contain both probe
arms with equal repetitions.  `public_transcript` and all unrelated state are
held fixed.  The primary evaluator excludes cases whose canonical transcript
hash differs between arms or whose swap is not both on-support and admissible.
[`records.example.jsonl`](records.example.jsonl) and
[`action_manifest.example.json`](action_manifest.example.json) are schema-only
fixtures, not experimental observations or gate evidence.

Required conditions are `active`, `visible_twin`, `dormant`, `disconnected`,
and `same_class_nuisance`; a full-logging oracle and off-manifold ablation may
be reported only as diagnostics.  The project gate additionally needs at least
two models or two suites and 50--100 paired cases with 8--16 repetitions per
arm where feasible.

```bash
python3 experiments/8.3_agentdojo/evaluate.py records.jsonl \
  --action-manifest experiments/8.3_agentdojo/action_manifest.example.json \
  --assignment-design complete_balanced_within_case \
  --output data/processed/8.3_agentdojo/action_boundary_summary.json
python3 -m unittest discover -s experiments/8.3_agentdojo -p 'test_*.py' -v
```

The generated summary is evidence for [`GO_NO_GO.md`](../../GO_NO_GO.md); it
is currently marked `partial_evaluation_not_gate_artifact` and cannot satisfy
the gate by itself. It does not promote `paper_v2/`, create a tag, or delete
legacy experiments.
The task-bootstrap percentile range around plug-in JS is descriptive and is
deliberately not named a confidence interval. The arm-label
randomization p-value tests only the sharp no-effect null under complete
balanced assignment. Use it only when that is the recorded assignment design;
a paired-swap design needs a paired randomization rule. Neither statistic is a
finite-sample lower certificate for gate criterion G5; that bound must be
implemented and reviewed before a GO decision.

The required action manifest projects raw structured calls onto a finite,
security-semantic alphabet and rejects unknown outcomes. Volatile fields such
as timestamps, request IDs, or model prose must not appear in that projection.
The current randomization test supports only complete balanced assignment
within each case. Its recorded `0.5` propensity is marginal; it must not be fed
to the sequential e-process, whose denominator is the true conditional probe
law at each round. A paired/common-randomness design needs a separate paired
randomization rule.

The evaluator weights unique public-transcript case strata equally and rejects
two case IDs sharing the same transcript hash. Interpreting the result as
transcript-conditioned information additionally requires that this uniform
case sampling match the declared deployment distribution. A transcript-arm
monitor beyond exact pair hashes and the G5 effect lower bound remain explicit
TODOs; marginal projected action distributions are included in the output.
Before real runs, preserve a reviewable assignment manifest containing the
randomization unit, assignment seed, and schedule hash; selecting the CLI's
design name does not prove that the declared randomization was executed.
Negative controls require prespecified equivalence margins or valid upper
bounds plus a multiplicity rule. A nonsignificant randomization test alone does
not establish the G6 null controls.
