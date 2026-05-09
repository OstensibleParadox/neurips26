# Lean 4 Artifact — Dual Certificates for Agent Audit

Mechanized core for Propositions 1–2 and Corollary 5 of the paper.

## What is checked

| Paper Item | Lean File | Theorem | Status |
|---|---|---|---|
| Corollary 5 (autoregressive zero-cut) | `Screenability.lean` | `no_eis_autoregressive` | C |
| Proposition 1 (static cut-sum bound) | `DualCertificate.lean` | `prop1_static_ub` | C/E |
| Proposition 2 (conditional DPI) | `DualCertificate.lean` | `prop2_dynamic_lb` | C/E |

C = fully mechanized from Mathlib first principles.  
C/E = structural reduction machine-checked conditional on 4 explicit axioms: `chain_rule`, `cut_set_bound`, `condMarkov`, `cond_dpi`.

## What is not formalized

Entropy, conditional entropy, and conditional mutual information are defined by finite-discrete formulas over `FinitePMF`, using Mathlib finite sums and real logarithms. The measure-theoretic chain rule, cut-set inequality, conditional Markovity, and conditional DPI are declared as the four explicit axioms consumed by the structural reductions.

## Build

Requires Lean 4 (`leanprover/lean4:v4.30.0-rc1`) and Mathlib.

```bash
cd verification
lake exe cache get   # strongly recommended: avoids cold Mathlib build (~30 min)
lake build           # expected: ~1–5 min with cache, 30–60 min without
```

`lake exe cache get` downloads prebuilt Mathlib dependency artifacts. On a machine without `elan`, install it first; it reads the pinned toolchain from `lean-toolchain` automatically.

## Module layout

- `FiniteQuerySandbox.InfoTheory` — finite PMF, finite-discrete entropy/conditional-MI definitions, conditional Markov/DPI axioms
- `FiniteQuerySandbox.Tools` — list/set utilities
- `FiniteQuerySandbox.DualCertificate` — Propositions 1–2 structural reductions
- `FiniteQuerySandbox.Screenability` — Corollary 5 (autoregressive zero-cut, fully mechanized)
- `FiniteQuerySandbox.ScreenabilityBridge` — legacy compatibility wrapper around the deterministic no-witness theorem
