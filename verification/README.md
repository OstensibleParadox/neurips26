# Lean Verification Artifact

This directory is a standalone Lean 4 package for the finite formal components
used in the paper.  The development centers on finite discrete probability,
finite-query impossibility, screenability surrogates, certificate reductions,
and covering/PAC algebraic cores.

## Build

From this directory:

```bash
lake exe cache get   # optional; downloads cached Mathlib artifacts when available
lake build
```

The package is pinned by `lean-toolchain` and `lake-manifest.json`.

## Checked Components

- `FiniteQuerySandbox.InfoTheory`: finite PMFs, entropy, conditional entropy,
  mutual information, conditional mutual information, finite KL nonnegativity,
  and finite-discrete conditional DPI.
- `FiniteQuerySandbox.IdentifiabilityGap`: axiom-free construction of two
  behaviorally equivalent but audit-inequivalent finite PMFs.
- `FiniteQuerySandbox.DualCertificate`: static and dynamic certificate
  reductions, including the explicit cut-set premise form and the auxiliary
  `log₂ |MissingTrace|` cardinality bound.
- `FiniteQuerySandbox.TraceRecoverability` and `TraceRecoverabilityBridge`:
  deterministic trace-recoverability core and compatibility theorem
  (legacy modules: `Screenability`, `ScreenabilityBridge`).
- `FiniteQuerySandbox.FiniteQueryDecisionImpossibility`,
  `PredictabilityRouteImpossibility`, and `SeparatedPackingImpossibility`:
  finite-query, predictability-route, and geometric non-covering impossibility
  arguments (legacy modules: `Impossibility`, `InternalImpossibility`,
  `GeometricImpossibility`).
- `FiniteQuerySandbox.CoveringBound`, `GeometricTools`, and `PACBounds`:
  covering-to-gap lemmas, finite representation-geometry utilities, and PAC
  algebraic lower-bound core.
- `FiniteQuerySandbox.QuotientFactorization`: reader-facing entry point for
  semantic-closure quotient factorization (legacy module:
  `SemanticClosureIff`).

## Naming Guide

- Migration aliases are provided so existing imports continue to work.
- Old `Screenability` -> new `TraceRecoverability`.
- Old `ScreenabilityBridge` -> new `TraceRecoverabilityBridge`.
- Old `SemanticClosureIff` -> new `QuotientFactorization`.
- Old `Impossibility` -> new `FiniteQueryDecisionImpossibility`.
- Old `InternalImpossibility` -> new `PredictabilityRouteImpossibility`.
- Old `GeometricImpossibility` -> new `SeparatedPackingImpossibility`.
- `FiniteQuerySandbox` is the historical package namespace retained for
  compatibility with existing imports and artifact references.

## Scope

The artifact mechanizes the finite discrete information-theory layer used by
the certificate reductions.  It keeps the cut-set inequality, conditional
Markovity as a modeling premise, and the statistical Fano/Gaussian-KL
derivations as explicit external assumptions or paper arguments.

Import `FiniteQuerySandbox` to check the full artifact. Import
`FiniteQueryAudit` for an alternate root name.
