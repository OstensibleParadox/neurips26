# Screenability

Anonymous artifact repository for the paper on the epistemic limits of
output-only certification in language models.

## Repository Layout

- `paper/`
  LaTeX source for the current manuscript and figure assets.
- `verification/`
  Reviewer-facing Lean 4 artifact for the checked proof cores.
- `experiments/6.1_cfsg/`
  Cross-Format Sensitivity Gap (CFSG) diagnostics for Section 6.1.
- `experiments/6.2_semantic_closure/`
  Lexical-substitution / semantic-closure experiments for Section 6.2.
- `configs/`
  Content definitions, prompts, and model lists used by the experiments.
- `data/`
  Minimal data needed for the checked paper tables, plots, and analysis scripts.
- `src/`
  Shared Python utilities used by the experiment pipelines.
- `scripts/`
  Small helper scripts used during reproduction.

## Quick Start

### Paper

```bash
cd paper
latexmk -pdf -interaction=nonstopmode main.tex
```

### Lean verification

```bash
cd verification
lake exe cache get   # optional: download prebuilt mathlib artifacts on a clean machine
lake build
```

### Experiment entry points

Run these from the repository root:

```bash
python3 -m pip install -r requirements.txt
python experiments/6.1_cfsg/compute_all_metrics.py
python experiments/6.1_cfsg/plot_figures.py
python experiments/6.2_semantic_closure/analyze_phase2a_ablation.py
```

Most experiment scripts assume repository-root-relative paths such as
`configs/...`, `data/...`, and `paper/figures/...`. Keep that layout unchanged
if you move or mirror this repository.

## Notes

- This export intentionally excludes local virtual environments, Hugging Face
  caches, assistant logs, LaTeX intermediates, and Lean build caches.
- The Python experiment scripts expect the packages listed in
  `requirements.txt`; missing `numpy`/`pandas`/`matplotlib` errors are
  environment issues, not repository path issues.
- The Lean artifact checks exact and surrogate proof cores, not the full
  information-theoretic library development.
- The experimental data included here are organized for paper reproduction, not
  as a polished benchmark release.
