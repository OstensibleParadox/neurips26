# FiniteQuerySandbox Lean Artifact

This directory is the reviewer-facing Lean 4 artifact for the formalized cores
used in the paper's verification appendix.

For a slightly more defensive build guide, including the case where the machine
does not already have Lean installed, see `LEAN_VERIFICATION.md`.

## Quick Build

From this directory:

```bash
lake exe cache get   # optional on a clean machine; avoids a full cold mathlib build
lake build
```

This directory is now the actual Lake package root; there is no nested source
tree to enter first.

## Toolchain

- Lean: `v4.30.0-rc1`
- Dependency: `mathlib4` via `lake-manifest.json`

## Module Map

- `FiniteQuerySandbox.IdentifiabilityGap`
  Theorem 1: Output-Trace Identifiability Gap — axiom-free construction of
  two behaviorally-equivalent but audit-inequivalent PMFs.
- `FiniteQuerySandbox.DualCertificate`
  Structural reductions for the static cut-sum bound and dynamic DPI bounds,
  built over finite-discrete entropy and conditional-MI definitions.
- `FiniteQuerySandbox.Screenability`
  Exact deterministic-screenability core for the internal route, including
  `projection_determined`, `projection_same_trace_eq`,
  `no_same_trace_projection_variation`, `no_same_trace_IA_witness`, and
  `no_eis_autoregressive`.
- `FiniteQuerySandbox.InternalImpossibility`
  `ε > 0` wrapper-level surrogate using predictability rather than entropy.
- `FiniteQuerySandbox.Impossibility`
  Finite-query soundness/completeness impossibility core.
- `FiniteQuerySandbox.SemanticClosureIff`
  Semantic closure and encoding-insensitivity equivalence.
- `FiniteQuerySandbox.CoveringBound`
  Pointwise covering-to-CFSG bound and high-probability lift.
- `FiniteQuerySandbox.PACBounds`
  PAC algebraic core, conditional on explicit external Fano and missed-cell
  premises.
- `FiniteQuerySandbox.GeometricImpossibility`
  Separated-packing non-covering lemma.

## Scope Notes

This artifact formalizes exact and surrogate cores, plus finite-discrete
entropy and conditional mutual information formulas. It does not derive the
measure-theoretic chain rule, cut-set inequality, conditional Markovity,
conditional DPI, or the statistical Fano / Gaussian-KL derivations.

## Layout

- `lakefile.lean`, `lean-toolchain`, `lake-manifest.json`
  Package entry point and pinned toolchain/dependency metadata.
- `FiniteQuerySandbox/*.lean`
  Source files for the formalization.
- `FiniteQuerySandbox.lean`
  Root import file for the library.
