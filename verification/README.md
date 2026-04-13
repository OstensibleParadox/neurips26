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

- `FiniteQuerySandbox.Screenability`
  Exact deterministic-screenability core for the internal route, including
  `projection_determined`, `projection_same_trace_eq`,
  `no_same_trace_projection_variation`, `no_same_trace_IA_witness`, and
  `no_eis_autoregressive`.
- `FiniteQuerySandbox.InternalImpossibility`
  `ε > 0` wrapper-level surrogate using predictability rather than entropy.
- `FiniteQuerySandbox.Impossibility`
  Finite-query soundness/completeness impossibility core.
- `FiniteQuerySandbox.CoveringBound`
  Pointwise covering-to-CFSG bound and high-probability lift.
- `FiniteQuerySandbox.PACBounds`
  PAC algebraic core, conditional on explicit external Fano and missed-cell
  premises.
- `FiniteQuerySandbox.GeometricImpossibility`
  Separated-packing non-covering lemma.

## Scope Notes

This artifact formalizes exact and surrogate cores, not the full
measure-theoretic or information-theoretic statements from the paper.
In particular, it does not directly formalize Shannon entropy, conditional
mutual information, or the statistical Fano / Gaussian-KL derivations.

## Layout

- `lakefile.lean`, `lean-toolchain`, `lake-manifest.json`
  Package entry point and pinned toolchain/dependency metadata.
- `FiniteQuerySandbox/*.lean`
  Source files for the formalization.
- `FiniteQuerySandbox.lean`
  Root import file for the library.
