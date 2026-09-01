# 8.2 Sequential Certificate

Status: **active, pre-go/no-go calibration**.

This experiment implements the predictable decoder e-process under an exact
conditional trace clamp:

```text
E_n = product_i g_i(Z_i | T_i,A_i;H_{i-1}) / pi_i(Z_i | H_{i-1}).
```

The decoder distribution is requested before the current randomized label is
used for fitting, and every design distribution must have full support.  The
implementation intentionally has no plug-in estimate of `q(Z|T)`: outside an
exact clamp, an estimated denominator would not retain the stated Ville
guarantee.

```bash
python3 experiments/8.2_sequential_certificate/run_calibration.py \
  --output data/processed/8.2_sequential_certificate/calibration.json
python3 -m unittest discover \
  -s experiments/8.2_sequential_certificate -p 'test_*.py' -v
```

The calibration output is evidence for individual gate rows, never an automatic
project-level GO decision.
This directory currently implements the witness-side e-process only. The
uniform transcript-only simulator upper certificate, its finite-sample
coverage, and the complete P2/N6 artifacts remain TODOs.
