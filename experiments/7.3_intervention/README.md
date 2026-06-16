# ReAct Intervention and Boundary Replay

This directory contains the ReAct module-level validation experiments for the
agent-audit certificate.

## Existing experiments

- `run_intervention.py` perturbs the hidden scratchpad and measures realized
  tool-action JS on dormant calculator tasks and active planning tasks.
- `run_replay.py` removes or partially reconstructs the scratchpad while holding
  the visible query fixed, then measures the soft tool-token distribution shift.
- `run_dormant_active.py` runs the dormant/active intervention split.

The checked-in paper result is intentionally conservative: ReAct controlled
replay changes soft tool-token probabilities, but the argmax tool counts remain
unchanged. This should be reported as a policy-readout diagnostic, not as the
main realized-action headline.

## Boundary-mined argmax validation

`run_boundary_replay.py` implements a boundary-sample mining pass:

1. Generate many ambiguous visible-query / hidden-scratchpad candidates.
2. Run only forward logits for the wild scratchpad condition.
3. Compute the top-1/top-2 margin over tool logits.
4. Keep low-margin candidates, e.g. margin `< 0.5` logits.
5. Re-evaluate scratchpad `remove`, `neutral`, and `counterfactual` conditions
   on the boundary set.
6. Report argmax flip rate, conditional JS bits, and bootstrap confidence
   intervals.

This targets the practical issue that ordinary tool-selection prompts are often
far from the decision boundary: the query alone strongly determines the tool,
so the scratchpad affects probabilities without flipping argmax. Boundary
mining asks whether the same module-level hidden state can produce realized
tool flips when the visible query is genuinely ambiguous.

## Usage

Zero-dependency dry-run candidate generation:

```bash
python3 experiments/7.3_intervention/run_boundary_replay.py \
  --dry-run \
  --max-candidates 25 \
  --output-dir /tmp/boundary_replay_smoke
```

Pilot run on a small candidate set:

```bash
python3 experiments/7.3_intervention/run_boundary_replay.py \
  --config experiments/7.3_intervention/configs/boundary_replay.yaml \
  --max-candidates 500 \
  --top-k-boundary 100
```

Production-style run on M4 Max:

```bash
python3 experiments/7.3_intervention/run_boundary_replay.py \
  --config experiments/7.3_intervention/configs/boundary_replay.yaml \
  --max-candidates 5000 \
  --margin-threshold 0.5 \
  --top-k-boundary 500
```

Run the same mining/evaluation protocol on an external candidate pool:

```bash
python3 experiments/7.3_intervention/run_boundary_replay.py \
  --config experiments/7.3_intervention/configs/boundary_replay.yaml \
  --candidates-jsonl data/react_boundary_candidates.jsonl
```

Each JSONL row should contain `visible_query`, `wild_scratchpad`, and optionally
`counterfactual_scratchpad`, `candidate_id`, `family`, `wild_tool`, and
`counterfactual_tool`.

The output directory contains:

- `boundary_candidates.jsonl`: all scored candidates and wild margins.
- `boundary_selected.jsonl`: selected low-margin boundary candidates.
- `boundary_eval.jsonl`: per-condition candidate results.
- `boundary_summary.json`: aggregate flip rates, JS bits, and CIs.

## Paper interpretation

If the boundary run produces a positive argmax flip rate, report it as
module-level realized-action validation for ReAct. It should not displace the
multi-agent private-report result as the strongest realized-action headline,
because the ReAct boundary set is deliberately mined from near-decision-boundary
queries.
