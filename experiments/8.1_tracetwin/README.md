# 8.1 TraceTwin

Status: **active, pre-go/no-go calibration laboratory**.

TraceTwin is the exact finite-alphabet model from
[`README_NEW_DIRECTION.md`](../../README_NEW_DIRECTION.md).  It has two
different regimes, which this implementation keeps separate:

- `passive`: the mediated and bypass mechanisms induce exactly the same
  visible law `P(T,A)`.  The bypass CMI is `h2(r)-h2(rho)`.
- `clamp`: the auditor randomizes `Z` while fixing `T=t`.  The bypass CMI is
  `1-h2(rho)`.

The controlled-clamp quantity must never be reported as the passive-twin
quantity. They generically have different numerical values, although the two
formulas happen to coincide at the boundary `p=1/2`; they remain different
audit regimes and estimands there.

Run the deterministic identities and a finite-sample passive baseline:

```bash
python3 experiments/8.1_tracetwin/run_calibration.py \
  --output data/processed/8.1_tracetwin/calibration.json
python3 -m unittest discover -s experiments/8.1_tracetwin -p 'test_*.py' -v
```

This directory establishes the exact model organism.  Repeated false-positive,
power, optional-stopping, and adaptive-probe calibration lives in
`../8.2_sequential_certificate/`.
The current runner checks exact identities and one passive held-out baseline;
confidence coverage, mixture monotonicity, repeated AUC uncertainty, and the
complete P1 artifact remain TODOs. Its output is therefore calibration, not a
gate summary.
