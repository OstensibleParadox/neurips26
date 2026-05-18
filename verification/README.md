# Lean Verification Artifact

This directory is a standalone Lean 4 package for the finite formal components
used in the paper.  The development centers on finite discrete probability,
information-theoretic certificate reductions, and the cut-set bound verification
pipeline.

## Build

```bash
lake exe cache get   # optional; caches Mathlib artifacts
lake build
```

Pinned by `lean-toolchain` and `lake-manifest.json`.

## Main Statements

| Paper item | Lean module | Declaration | Status |
|---|---|---|---|
| Definition 1 — Core audit quantities | `DualCertificate` | `H_S_cond_Ttilde`, `delta_act` | Fully mechanized |
| Remark 1 — Complementarity / inheritance | (conceptual, follows from DPI ordering) | — | Implied by `prop2_dynamic_lb` ≤ |·| bound |
| Lemma 1 — Additive decomposition (software orthogonality) | `DualCertificate` | `static_decomposition`, `software_orthogonal` | Fully mechanized |
| Proposition 1 — Static certificate via cut-set bound | `DualCertificate` | `prop1_static_ub` | From cut-set premise |
| Corollary 1 — Additive min-cut form | `DualCertificate` | `corollary_additive_ub` | From cut-set premise + orthogonality hypothesis |
| Corollary 2 — Autoregressive zero-cut | `Screenability` | `no_eis_autoregressive` | Fully mechanized |
| Proposition 2 — Probe certificates from conditional DPI | `DualCertificate` | `prop2_dynamic_lb`, `aggregated_dynamic_lb` | From finite DPI |
| Leaf marginalization helper for DAG elimination | `InfoTheory` | `marginalizeLeafPMF`, `sum_leaf_pmf_eq_subgraph_pmf` | Fully mechanized helper |
| Static cardinality corollary (`ε_state^UB ≤ H_nominal + log|Missing|`) | `DualCertificate` | `prop1_static_ub_bounded` | Fully mechanized |
| Cut-set DPI bottleneck (`I(S;M|T̃) ≤ I(Y;Z|W)`) | `CutSetBoundExtract` | `abstract_cut_set_bound` | From cut-set premise |
| KKT certificate capacity bound (`I(Y;Z|W) ≤ C`) | `ChannelCapacity` | `KKT_Certificate`, `capacity_le_of_kkt` | From per-symbol KKT condition |
| Linear chain cut-set bound (`ε_state^UB ≤ 1 bit`) | `CaseStudy` | `linear_chain_cut_set_bound` | KKT cert + DPI + `abstract_cut_set_bound` |
| Deterministic trace recoverability | `TraceRecoverability` | `no_internal_witness_trace_recoverability` | Fully mechanized |
| Behavioral equivalence ≠ audit equivalence | `IdentifiabilityGap` | `identifiability_gap_extremes` | Fully mechanized |
| DAG d-separation predicates and graph pipeline | `DAGParser` | `dSeparates`, `Trail.isBlocked`, `DAG.dSeparated`, `DAG.moralGraph` | Partially mechanized |
| DAG Markov condition generation | `MarkovGenerator` | `computeMarkovBlanket`, `generateMarkovConditions` | Partially mechanized |
| d-sep ⇒ conditional independence bridge | `MarkovGenerator` | `factorizes_dsep_implies_cond_indep`, `condMarkov_of_factorizes_dsep_fourVar` | Semantic bridge plus four-variable `condMarkov` adapter; full Verma-Pearl theorem not claimed |

## Module Map

### Information-Theoretic Core

- **`InfoTheory.lean`** — `FinitePMF`, Shannon entropy (bits), conditional entropy,
  mutual information, conditional mutual information, finite KL nonnegativity,
  entropy cardinality bound, `condMarkov` factorization, conditional DPI
  (`cond_dpi` proved from first principles).  It also contains the leaf
  marginalization helper `marginalizeLeafPMF` and
  `sum_leaf_pmf_eq_subgraph_pmf`, used to isolate the local sum-out step needed
  by a future Verma-Pearl leaf-elimination proof.

- **`InfoTheoryHelpers.lean`** — `IsMarkovChain`, chain rule identities,
  `cond_mutual_info_zero_of_markov`, `data_processing_inequality`.

- **`CMI_Nonneg.lean`** — Bridges `condMutualInfo_nonneg` for unconditional CMI.

### Cut-Set Bound Pipeline

- **`CutSetBoundExtract.lean`** — `pmf_from_vars` pushforward, marginal equivalence
  lemmas, `cut_set_dpi_bound` (DPI bottleneck theorem), `abstract_cut_set_bound`
  (final inequality chain), `prop1_static_ub_from_cut`.

- **`ChannelCapacity.lean`** — `KKT_Certificate` structure (p_star, per-symbol
  bounds, KKT condition), `capacity_le_of_kkt` (weighted-average bound from KKT).

- **`CaseStudy.lean`** — Linear chain S→Y→M (State=CUtVar=Missing=`Fin 2`,
  VisibleTrace=`Unit`). Proves `I_YZ_W ≤ log₂|CutVars| = 1` bit via
  `condEntropy_nonneg` and `entropy_le_log_card`.  Composes through
  `KKT_Certificate` → `abstract_cut_set_bound` → `I(S;M|T̃) ≤ 1`.

### Certificate Reductions & Archive

- **`DualCertificate.lean`** — Static (`prop1_static_ub`,
  `prop1_static_ub_bounded`) and dynamic (`prop2_dynamic_lb`,
  `aggregated_dynamic_lb`) certificate theorems, entropy decomposition,
  `H_S_cond_Ttilde` / `I_S_M_cond_Ttilde` definitions.

- **`DAGParser.lean`** — `structure DAG`, `IsLeaf`,
  `exists_leaf_of_nonempty`, parent/child/ancestor/descendant queries,
  rank-based DAG construction helper, trail-blocking `dSeparates`, and the
  ancestral-subgraph/moralization criterion (`DAG.ancestralSubgraph`,
  `DAG.moralGraph`, `DAG.dSeparationGraph`, `DAG.dSeparated`).  The graph
  conversion pipeline is now represented in Lean; the equivalence between the
  trail predicate and the moralized-ancestral criterion, plus a certified
  decision procedure, remains open.

- **`MarkovGenerator.lean`** — `computeMarkovBlanket`, `spouses`,
  `generateMarkovConditions`, `generateMarkovBlanketConditions`,
  `FactorizesOverDAG`, `factorizes_dsep_implies_cond_indep`,
  `condMarkovNodeCI`, and `condMarkov_of_factorizes_dsep_fourVar`.  The bridge
  is semantic: `FactorizesOverDAG` packages the model-specific conditional
  independence predicate, and the four-variable adapter extracts the concrete
  `condMarkov` equation for `{0} ⟂ {2} | {1,3}`.  It still does not assert the
  full Verma-Pearl global Markov theorem from graph structure alone.

- **`IdentifiabilityGap.lean`** — Axiom-free construction of two behaviorally
  equivalent but audit-inequivalent finite PMFs.

- **`TraceRecoverability.lean`**, **`TraceRecoverabilityBridge.lean`** —
  Deterministic trace-recoverability core and compatibility theorem.

### Impossibility Cores (Archive)

- **`FiniteQueryDecisionImpossibility.lean`**, **`PredictabilityRouteImpossibility.lean`**,
  **`SeparatedPackingImpossibility.lean`** — Finite-query, predictability-route,
  and geometric non-covering impossibility arguments.

### Auxiliary

- **`CoveringBound.lean`**, **`GeometricTools.lean`**, **`PACBounds.lean`** —
  Covering-to-gap lemmas, representation geometry, PAC algebraic core.

- **`QuotientFactorization.lean`** — Semantic-closure quotient factorization.

- **`Tools.lean`**, **`QuantizedBound.lean`** — Shared utilities.

## Architecture Overview

The verification pipeline has three layers:

```
             ┌─────────────────────────────────────┐
  DAG/Markov │ DAGParser + MarkovGenerator          │  ← Stages 1–2 in progress
  automation │ (d-separation, moralization, blanket,│     (DAGParser.lean,
             │  FactorizesOverDAG)                  │      MarkovGenerator.lean)
             └─────────────────────────────────────┘
                         ↓ semantic CI predicate → four-variable condMarkov adapter
             ┌─────────────────────────────────────┐
  Cut-set    │ pmf_from_vars → cut_set_dpi_bound    │  ← CutSetBoundExtract.lean
  bound      │ → abstract_cut_set_bound            │     (implemented)
             │                                      │
             └─────────────────────────────────────┘
                         ↓ h_cap : I_YZ_W(P4) ≤ C
             ┌─────────────────────────────────────┐
  KKT cert   │ KKT_Certificate → capacity_le_of_kkt  │  ← ChannelCapacity.lean
             │ (weighted average)                   │     (implemented)
             └─────────────────────────────────────┘
```

The current implementation plan and remaining proof obligations are documented
in [`stage-1-dag-concurrent-cerf.md`](./stage-1-dag-concurrent-cerf.md).

Currently, `condMarkov` is still verified directly on the pushforward PMF
in the original case-study theorem.  A new case-study theorem,
`linear_chain_cut_set_bound_from_dag`, routes through the DAG interface:
`FactorizesOverDAG` plus a d-separation proof for `{0} ⟂ {2} | {1,3}` yields
the concrete four-variable `condMarkov` premise required by the DPI layer.
The moralization predicate `DAG.dSeparated` is available as the graph-conversion
criterion, but it is not yet connected by theorem to the older trail predicate
used by this adapter.

## External Premises

The artifact leaves the following as explicit assumptions:

- **cut-set/information-flow inequality** — premise of `prop1_static_ub`;
  the `ChannelCapacity` module provides a KKT-certificate verification path for
  concrete instances.
- **conditional Markovity** — structural modeling premise (`condMarkov` is
  defined algebraically and verified directly in the original case study; the
  four-variable DAG adapter is implemented, while a generic full-assignment
  DAG factorization theorem remains open).  The leaf-existence and
  leaf-marginalization helpers are implemented, but the full Verma-Pearl
  induction that repeatedly sums out leaves is not yet formalized.
- **statistical Fano and Gaussian-KL derivations** — used by the PAC lower-bound
  narrative (paper argument, not formalized).

All other information-theoretic claims (chain rule, DPI, entropy nonnegativity,
CMI nonnegativity) are proved from Mathlib first principles over finite-discrete
`FinitePMF` definitions.

## Naming Guide

| Legacy name | Current name |
|---|---|
| `Screenability` | `TraceRecoverability` |
| `ScreenabilityBridge` | `TraceRecoverabilityBridge` |
| `SemanticClosureIff` | `QuotientFactorization` |
| `Impossibility` | `FiniteQueryDecisionImpossibility` |
| `InternalImpossibility` | `PredictabilityRouteImpossibility` |
| `GeometricImpossibility` | `SeparatedPackingImpossibility` |

`FiniteQuerySandbox` is the historical package namespace retained for compatibility.

## Verification Status

```bash
lake build   # all 8300+ jobs pass
```

Import `FiniteQuerySandbox` to check the full artifact.

## Remaining Stages (Future Work)

The full formalization plan (4 stages) is partially implemented
(implementation plan: [`stage-1-dag-concurrent-cerf.md`](./stage-1-dag-concurrent-cerf.md)):

| Stage | Module | Status | Target |
|---|---|---|---|
| 1 — DAG predicate semantics & topological order | `DAGParser.lean` | Partially implemented | DAG structure, `WellFounded` acyclicity, leaf existence, `Trail`/`dSeparates`, ancestral-subgraph/moralization `DAG.dSeparated`; trail↔moralization equivalence and certified decision procedure pending |
| 2 — Markov semantics bridge & automation | `MarkovGenerator.lean` | Partially implemented | Markov blanket and condition generation plus semantic bridge and four-variable `condMarkov` adapter; full Verma-Pearl proof pending |
| 3 — Channel capacity & KKT certificate verification | `ChannelCapacity.lean` | Completed | `KKT_Certificate` + `capacity_le_of_kkt` (BA iteration not formalized) |
| 4 — Linear chain end-to-end verification | `CaseStudy.lean` | Completed | Linear chain S→Y→M → `abstract_cut_set_bound` |

Stages 1–2 are now started in Lean.  They provide an alternate case-study entry
point that replaces the raw `condMarkov` hypothesis with
`FactorizesOverDAG + dSeparates` for the existing four-variable tuple layout.
They also provide the moralized ancestral graph predicate `DAG.dSeparated` and
the local leaf-sum PMF helper needed for a Verma-Pearl induction.  The remaining
open part is stronger: deriving `FactorizesOverDAG` itself from a probabilistic
DAG factorization theorem rather than assuming it semantically, and proving the
equivalence between the two d-separation presentations.

Stage 3's KKT framework is structurally ready for non-trivial certificates;
the full Blahut-Arimoto convergence proof and concave KKT sufficiency
metatheorem remain as open work.
