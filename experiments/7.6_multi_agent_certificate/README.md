# Experiment 7.6: Multi-Agent Private-Report Certificate

Purpose: test whether the dynamic certificate can detect a high-decision-relevance
hidden channel in a two-agent deployment. A worker sees the benchmark item and
writes a private evidence report. The controller sees only that report and must
choose one API from `{calculator, search}`.

## Design

- Task pool: 200 `openai/gsm8k` `main` train items mapped to `calculator`,
  plus 200 `hotpotqa/hotpot_qa` `distractor` validation items mapped to
  `search`; seed `42`.
- Worker: local Ollama `llama3.1:8b-instruct-q4_K_M`.
- Controller: local Ollama `qwen2.5:7b-instruct-q4_K_M`.
- Samples: `k=8` controller generations per task and condition.
- Estimator: per-task JS divergence in bits, then task-block bootstrap 95% CI.

The main paper row is the counterfactual evidence intervention. Direct private
labels are implemented only as an oracle-tag upper-bound row.

## Conditions

- `wild`: the worker report generated from the task.
- `neutral_replay`: a length-matched neutral filler report.
- `counterfactual_evidence`: a worker report from the opposite task class.
- `same_class_shuffle`: a worker report from another task in the same class.
- `oracle_tag_correct` / `oracle_tag_flipped`: direct private tags for the
  appendix upper-bound contrast.

## Run

Pilot:

```bash
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --n-per-class 20 \
  --k-samples 8 \
  --out-dir data/processed/multi_agent_certificate_pilot
```

Full run (parallel workers, oracle tags mocked as upper-bound):

```bash
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --n-per-class 200 \
  --k-samples 8 \
  --workers 3 \
  --out-dir data/processed/multi_agent_certificate
```

If Hugging Face data are already cached, the run can be split:

```bash
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --stage prepare --n-per-class 200
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --stage reports
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --stage actions
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --stage analyze
```

Fast smoke test without datasets or Ollama:

```bash
python experiments/7.6_multi_agent_certificate/run_multi_agent_certificate.py \
  --mock \
  --tasks-jsonl experiments/7.6_multi_agent_certificate/smoke_tasks.jsonl \
  --n-per-class 2 \
  --k-samples 2 \
  --bootstrap 100 \
  --out-dir /tmp/multi_agent_certificate_smoke
```

## Output

- `tasks.jsonl`: sampled benchmark task pool.
- `reports.jsonl`: raw worker responses and parsed private reports.
- `report_leak_audit.json`: banned-term leakage audit for worker reports.
- `actions.jsonl`: raw controller samples and parsed labels.
- `per_task_js.jsonl` / `.csv`: JS values by task and contrast.
- `summary.json`: bootstrap summary and parse-failure rate.
- `summary.csv`: compact contrast-level summary.
- `summary_table.tex`: generated LaTeX table for local inspection; the paper
  source uses `experiments/render_paper_tables.py` to render
  `paper/tables/multi_agent_dynamic.tex` from `summary.json`.
