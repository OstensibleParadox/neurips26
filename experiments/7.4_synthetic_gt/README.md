# 7.4 Synthetic Ground Truth

Status: **noise/true-MI mismatch repaired; historical estimator results remain
withdrawn**.

The generator samples independent Gaussian logit noise.  The ground-truth
target now evaluates

```text
q_h(a|T) = E_noise softmax(TW + beta_h * h * e_0 + noise)
```

and computes the balanced conditional JS directly from `q_0` and `q_1`.
Sampled hidden states and actions are not inputs to the target calculation.
Mechanism, context, action, and integration randomness use separate streams.
For nonzero noise, `q_h` is still an inner Monte Carlo approximation; report
its sample count and check stability across integration seeds before using it
as a numerical reference.

Run the regression suite and a ground-truth-only calibration with:

```bash
python3 -m unittest discover \
  -s experiments/7.4_synthetic_gt -p 'test_*.py' -v

python3 experiments/7.4_synthetic_gt/run_synthetic.py \
  --ground-truth-only \
  --noise-std 0.1 \
  --gt-inner-samples 8192 \
  --out-dir /tmp/synthetic_gt_repaired
```

[`V3_POSITIVE_CONTROL.md`](V3_POSITIVE_CONTROL.md) is a withdrawn historical
record.  Its old estimator tables and conclusions are not a certificate and
are not evidence for the v2 go/no-go gate.  Repaired estimator runs require a
new review before this directory can serve as validation evidence.
