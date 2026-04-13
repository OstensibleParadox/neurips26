# Screenability Manifest

This manifest maps the repository contents to the paper and the reviewer-facing
artifact workflow.

## Main Components

| Component | Purpose | Primary entry points |
|-----------|---------|----------------------|
| `paper/` | Manuscript source and figures | `paper/main.tex` |
| `verification/` | Lean 4 formalization artifact | `verification/README.md`, `verification/LEAN_VERIFICATION.md` |
| `experiments/6.1_cfsg/` | CFSG diagnostics for Section 6.1 | `compute_all_metrics.py`, `plot_figures.py`, `run_statistical_tests.py` |
| `experiments/6.2_semantic_closure/` | Semantic-closure and lexical-substitution analysis for Section 6.2 | `run_phase1.py`, `run_phase2a.py`, `analyze_phase2a_ablation.py` |
| `data/compiled/` | Aggregated outputs used by tables and figures | section-specific CSV/JSON outputs |
| `data/episodes/` | Episode text used in the semantic-closure experiment | text files for phase construction |
| `data/manual_web/` | Manual web packet for diffusion-family import path | manual packet + manifest |
| `src/` | Shared utility code | metrics, sampling, models, utils |

## Paper Section Map

- Section 6.1:
  `experiments/6.1_cfsg/`, `configs/format_content_instances.jsonl`,
  `data/compiled/`, `paper/figures/`
- Section 6.2:
  `experiments/6.2_semantic_closure/`, `data/episodes/`, `data/raw/semantic_closure/`,
  `data/compiled/session_structure/`
- Lean appendix:
  `verification/`

## Reproduction Notes

- Paper compilation is run from `paper/`.
- Lean verification is run from `verification/`.
- Python experiment scripts are run from the repository root and rely on the
  existing relative layout of `configs/`, `data/`, `paper/`, and `src/`.
- Python dependencies are listed in `requirements.txt`; the expected failure
  mode on a bare machine is a missing-package import such as `numpy`, not a
  broken path layout inside the repository.
- The included `data/manual_web/` packet uses repo-relative output targets so
  that `import_manual_web_outputs.py` can be rerun inside this anonymous export.

## Excluded Local Artifacts

This anonymous export omits:

- local virtual environments and package vendor directories;
- Hugging Face and model caches;
- assistant logs and editor metadata;
- LaTeX intermediates and compiled PDFs;
- Lean `.lake/` build caches.
