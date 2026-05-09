# Verification Status

This package checks the Lean formalization supporting the paper's finite
verification claims.

## Main Statements

| Paper item | Lean module | Declaration | Status |
|---|---|---|---|
| Identifiability gap | `IdentifiabilityGap` | `identifiability_gap_extremes` | Fully mechanized |
| Static certificate reduction | `DualCertificate` | `prop1_static_ub` | Mechanized from explicit cut-set premise |
| Static cardinality corollary | `DualCertificate` | `prop1_static_ub_bounded` | Fully mechanized |
| Dynamic certificate reduction | `DualCertificate` | `prop2_dynamic_lb` | Fully mechanized from finite DPI |
| Deterministic trace recoverability | `TraceRecoverability` | `no_internal_witness_trace_recoverability` | Fully mechanized |

## Naming Notes

- New reader-facing modules:
  `TraceRecoverability`, `TraceRecoverabilityBridge`,
  `QuotientFactorization`, `FiniteQueryDecisionImpossibility`,
  `PredictabilityRouteImpossibility`, and `SeparatedPackingImpossibility`.
- Legacy modules remain supported:
  `Screenability`, `ScreenabilityBridge`, `SemanticClosureIff`,
  `Impossibility`, `InternalImpossibility`, and `GeometricImpossibility`.
- `FiniteQueryAudit` is provided as an alias root module that re-exports
  `FiniteQuerySandbox`.

## Information-Theory Layer

`InfoTheory.lean` defines finite PMFs, Shannon entropy in bits, conditional
entropy, mutual information, conditional mutual information, and finite KL
terms over real-valued finite sums.  It proves the finite KL nonnegativity
lemmas, entropy cardinality bound, conditional mutual information
nonnegativity, and conditional DPI used by the certificate reductions.

## External Premises

The artifact deliberately leaves the following as explicit assumptions or paper
arguments:

- the cut-set/information-flow inequality used as the premise of
  `prop1_static_ub`;
- conditional Markovity when used as a modeling assumption;
- statistical Fano and Gaussian-KL derivations used by the PAC lower-bound
  narrative.

## Reproducibility

```bash
cd verification
lake exe cache get
lake build
```

The root module `FiniteQuerySandbox` imports all checked modules. You can also
import `FiniteQueryAudit` as an alternate entry name.
