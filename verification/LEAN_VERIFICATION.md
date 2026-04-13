# Lean 4 Verification Note

This document records the current Lean 4 supplement for the screenability
paper's formal verification artifact in:

`verification/`

The checked artifact covers four proof-critical fragments of the paper:

- the indexed finite-query non-exhaustion / impossibility core;
- the deterministic and predictability-based screenability core for internal-state witnesses;
- the algebraic and decision-theoretic core of the separated-cell PAC packing lower bound;
- the pointwise geometric upper bound for the cross-format sensitivity gap.

It does not claim to formalize Shannon entropy, conditional mutual
information, the full semantic-quotient construction over arbitrary encoding
spaces, or the Gaussian KL / Fano derivations used as external statistical
ingredients.

## Build

The reviewer-facing build command is:

```bash
cd verification
lake exe cache get   # optional on a clean machine; downloads prebuilt dependency artifacts
lake build
```

This directory is the actual Lake package root. No further `cd` into a nested
Lean directory is required.

Current toolchain:

```text
leanprover/lean4:v4.30.0-rc1
```

The package depends on Mathlib via the checked-in `lake-manifest.json`.

## Why the internal route is simplified here

The paper states the internal route in information-theoretic language:
conditional entropy, conditional mutual information, and a DPI chain. The Lean
artifact does not rebuild that full layer. Instead, it checks the proof
skeleton at two lighter levels:

- an exact same-trace surrogate for the `epsilon = 0` autoregressive core;
- a predictability surrogate for the `epsilon > 0` wrapper case.

The reason is the same one used elsewhere in the supplement. In the PAC lower
bound, the algebraic reduction is checked, while Gaussian KL and Fano are left
external. Here, the exact and predictability obstructions are checked, while
the heavier measure-theoretic entropy / CMI machinery is left external. The
goal of the artifact is to machine-check the proof-critical skeleton, not to
rebuild all of information theory inside Lean.

## Environment Note

The artifact assumes a standard Lean 4 environment managed by `elan`. On a
machine where `lake` is unavailable, the failure is environmental rather than a
project-specific build problem: the Lean toolchain manager is not installed or
is not on `PATH`. In the usual setup, installing `elan` is sufficient; it will
fetch the pinned Lean toolchain automatically from `lean-toolchain` on first
use. No separate manual Lean version selection is required beyond that.

## Default Target

The default target imports the checked core:

```lean
import FiniteQuerySandbox.Tools
import FiniteQuerySandbox.Impossibility
import FiniteQuerySandbox.GeometricTools
import FiniteQuerySandbox.GeometricImpossibility
import FiniteQuerySandbox.CoveringBound
import FiniteQuerySandbox.InternalImpossibility
import FiniteQuerySandbox.PACBounds
import FiniteQuerySandbox.Screenability
```

## Paper-to-Lean Map

### Finite-Query Core

File: `FiniteQuerySandbox/Impossibility.lean`

Checked declarations:

- `finite_patch_cannot_complete`: every finite support list misses some natural-number index.
- `infinite_residual_indices`: above every cutoff there remains a fresh unseen index.
- `encoded_fresh_not_mem`: injective encodings lift freshness from indices to encoded objects.
- `encoded_infinite_residual`: injective encodings leave infinitely many residual encoded objects.
- `finite_query_impossibility`: no stable finite-query closure certifier is both sound and complete.

This formalizes the indexed finite-query core only. It does not by itself prove
semantic equivalence for arbitrary natural-language encoding spaces,
deployment relevance, or quantitative off-support lower bounds.

### Internal Screenability Core

File: `FiniteQuerySandbox/Screenability.lean`

Checked declarations:

- `DeterministicScreen`: exact deterministic screenability of the operative state from the audit trace.
- `projection_determined`: any admissible projection of a deterministically screened state is also trace-determined.
- `projection_same_trace_eq`: trace-equivalent outcomes force projected internal states to agree.
- `no_same_trace_projection_variation`: same-trace residual-variation witnesses are impossible under deterministic screenability.
- `no_same_trace_IA_witness`: same-trace `(I, A)` witness patterns are blocked by the same exact-core obstruction.
- `ExactEISWitness`: exact operational surrogate for the paper's internal-state witness definition.
- `no_eis_autoregressive`: no exact internal-state witness exists under deterministic screenability of the full operative state.

This is an exact discrete surrogate of the paper's `epsilon = 0` internal
route. It is closer to the proof route than the earlier vacuous formulation,
but it is still not a direct formalization of entropy or conditional mutual
information.

File: `FiniteQuerySandbox/InternalImpossibility.lean`

Checked declarations:

- `ProbSpace`: minimal normalized monotone set-function interface; not a full sigma-additive probability space.
- `IsPredictable`: predictability surrogate replacing conditional-entropy screenability.
- `IsEISWitness`: operational `epsilon > 0` witness predicate with endogeneity, predictability-based residual autonomy, and same-trace covariation relevance surrogate.
- `screenability_lemma_predictability`: predictability of the full state propagates through admissible projections.
- `internal_impossibility_predictability`: under `eps < eps_min`, no operational `IsEISWitness` can exist.

This proves a predictability-based wrapper surrogate for the paper's
deployment-relative `epsilon > 0` argument. It does not formalize the full
information-theoretic DPI chain from the paper.

### PAC Packing Core

File: `FiniteQuerySandbox/PACBounds.lean`

Checked declarations:

- `PairwiseSeparated`: abstract pairwise separation condition for a hypothesis family.
- `spikeL1Distance`: exact `L1(Px)` distance table for the spike reward family.
- `spike_family_separated`: the spike family is separated at scale `alpha * tau`.
- `TriangleAgainstFamily`: triangle-inequality interface needed for nearest-neighbor decoding.
- `separated_success_makes_true_unique_nearest`: success at `epsilon < sep / 4` forces the true hypothesis to be the unique nearest one.
- `pac_success_identifies_index`: PAC success induces correct hidden-index recovery.
- `combine_fano_and_missed_cell_bounds`: algebraic combination of the Fano and missed-cell lower-bound terms.
- `AssumesFanoBound` / `AssumesMissedCellBound`: explicit wrappers for the external statistical premises.
- `PACStatisticalPremises`: combined external statistical premise interface.
- `pac_lower_bound_conditional`: conditional PAC lower bound wrapper.
- `theorem3_pac_lower_bound`: paper-facing alias for the checked conditional lower-bound core.

The reduction from reward estimation to index recovery and the algebraic
combination of lower-bound terms are checked. The Gaussian KL and Fano /
missed-cell probabilistic derivations remain external.

### Geometric FCG Core

File: `FiniteQuerySandbox/GeometricTools.lean`

Checked declarations:

- `NormalizedReprDist`
- `ReprSim`
- `IsRhoCover`
- `LipschitzOnRepresentation`
- `FCG`
- `GoodFCGSet`
- `HighProbRegion`
- `reprSim_mem_unitInterval`

File: `FiniteQuerySandbox/GeometricImpossibility.lean`

Checked declarations:

- `IsGammaSeparatedInjection`
- `packing_lemma`
- `finite_patch_cannot_cover_separated`

File: `FiniteQuerySandbox/CoveringBound.lean`

Checked declarations:

- `fcg_covering_bound`
- `subset_goodFCGSet_of_cover`
- `goodFCGSet_compl_mass_le`
- `goodFCGSet_highProb`
- `goodFCGSet_mass_ge_one_sub_eps_of_cover`

This aligns with the pointwise upper-bound direction of the geometric
stability section while separating the checked pointwise theorem from the
probabilistic high-mass corollaries.
