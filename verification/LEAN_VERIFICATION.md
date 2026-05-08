# Lean 4 Artifact — Dual Certificates for Agent Audit

Mechanized core for Propositions 1–2 and Corollary 5 of the paper.

## What is checked

| Paper Item | Lean File | Theorem | Status |
|---|---|---|---|
| Corollary 5 (autoregressive zero-cut) | `Screenability.lean` | `no_eis_autoregressive` | C |
| Proposition 1 (static cut-sum bound) | `DualCertificate.lean` | `prop1_static_ub` | C/E |
| Proposition 2 (conditional DPI) | `DualCertificate.lean` | `prop2_dynamic_lb` | C/E |
| Bridge (EIS → zero-cut) | `ScreenabilityBridge.lean` | `no_eis_implies_zero_cut` | C/E |

C = fully mechanized from Mathlib first principles.  
C/E = structural reduction machine-checked conditional on 4 explicit axioms: `chain_rule`, `cut_set_bound`, `condMarkov`, `cond_dpi`.

## What is not formalized

Shannon entropy, conditional mutual information, and the measure-theoretic DPI chain are declared as axioms. The artifact verifies the structural reductions — that the paper's propositions follow from these axioms — but does not rebuild information theory inside Lean.

## Build

Requires Lean 4 (`leanprover/lean4:v4.30.0-rc1`) and Mathlib.

```bash
cd verification
lake exe cache get   # strongly recommended: avoids cold Mathlib build (~30 min)
lake build           # expected: ~1–5 min with cache, 30–60 min without
```

`lake exe cache get` downloads prebuilt Mathlib dependency artifacts. On a machine without `elan`, install it first; it reads the pinned toolchain from `lean-toolchain` automatically.

## Module layout

- `FiniteQuerySandbox.InfoTheory` — finite PMF, entropy/MI stub definitions, 4 declared axioms
- `FiniteQuerySandbox.Tools` — list/set utilities
- `FiniteQuerySandbox.DualCertificate` — Propositions 1–2 structural reductions
- `FiniteQuerySandbox.Screenability` — Corollary 5 (autoregressive zero-cut, fully mechanized)
- `FiniteQuerySandbox.ScreenabilityBridge` — equivalence bridge from screenability to zero-cut
