# Lean Verification Artifact

<!--
LEAN ARTIFACT README.

For the POPL27 probability-sheaf theory, see
`../popl27_magwalk_sheaf_bridge.md`. This README documents the current Lean
artifact. In this artifact, `MAGWalk` is graph-level; any enriched
probability/sheaf version should be introduced as a separate structure such as
`SheafMAGWalk` and projected down to the current checked `MAGWalk`.
-->

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

```bash
lake build   # all 8310+ jobs pass, zero sorries
```

## Main Statements

| Paper item                                                               | Lean module                 | Declaration                                                                                                                            | Status                                                                                                       |
| ------------------------------------------------------------------------ | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Definition 1 — Core audit quantities                                     | `DualCertificate`           | `H_S_cond_Ttilde`, `delta_act`                                                                                                         | Fully mechanized                                                                                             |
| Remark 1 — Complementarity / inheritance                                 | (follows from DPI ordering) | —                                                                                                                                      | Implied by `prop2_dynamic_lb` ≤ \|·\| bound                                                                  |
| Lemma 1 — Additive decomposition (software orthogonality)                | `DualCertificate`           | `static_decomposition`, `software_orthogonal`                                                                                          | Fully mechanized                                                                                             |
| Proposition 1 — Static certificate via cut-set bound                     | `DualCertificate`           | `prop1_static_ub`                                                                                                                      | Fully mechanized (explicit hypotheses)                                                                       |
| Corollary 1 — Additive min-cut form                                      | `DualCertificate`           | `corollary_additive_ub`                                                                                                                | Fully mechanized (explicit hypotheses)                                                                       |
| Corollary 2 — Autoregressive zero-cut                                    | `TraceRecoverability`       | `no_eis_autoregressive`                                                                                                                | Fully mechanized                                                                                             |
| Proposition 2 — Probe certificates from conditional DPI                  | `DualCertificate`           | `prop2_dynamic_lb`, `aggregated_dynamic_lb`                                                                                            | Fully mechanized (explicit hypotheses)                                                                       |
| Static cardinality corollary (`ε_state^UB ≤ H_nominal + log\|Missing\|`) | `DualCertificate`           | `prop1_static_ub_bounded`                                                                                                              | Fully mechanized                                                                                             |
| Cut-set DPI bottleneck (`I(S;M\|T̃) ≤ I(Y;Z\|W)`)                        | `CutSetBoundExtract`        | `abstract_cut_set_bound`                                                                                                               | Fully mechanized (explicit hypotheses)                                                                       |
| KKT certificate capacity bound (`I(Y;Z\|W) ≤ C`)                         | `ChannelCapacity`           | `KKT_Certificate`, `capacity_le_of_kkt`                                                                                                | Fully mechanized (explicit hypotheses)                                                                       |
| Linear chain cut-set bound (`ε_state^UB ≤ 1 bit`)                        | `CaseStudy`                 | `linear_chain_cut_set_bound`                                                                                                           | Fully mechanized (explicit hypotheses)                                                                       |
| Linear chain via DAG interface                                           | `CaseStudy`                 | `linear_chain_cut_set_bound_from_dag`                                                                                                  | `FactorizesOverDAG` + `dSeparates` → `condMarkov` → bound                                                    |
| Leaf marginalization helper                                              | `InfoTheory`                | `marginalizeLeafPMF`, `sum_leaf_pmf_eq_subgraph_pmf`                                                                                   | Fully mechanized helper                                                                                      |
| Deterministic trace recoverability                                       | `TraceRecoverability`       | `no_internal_witness_trace_recoverability`                                                                                             | Fully mechanized                                                                                             |
| Behavioral equivalence ≠ audit equivalence                               | `IdentifiabilityGap`        | `identifiability_gap_extremes`                                                                                                         | Fully mechanized                                                                                             |
| DAG infrastructure, trail d-separation, moralized ancestral graph        | `DAGParser`                 | `dSeparates`, `Trail.isBlocked`, `DAG.dSeparated`, `DAG.moralGraph`                                                                    | Fully mechanized                                                                                             |
| Standard d-separation query domain                                       | `DAGParser`                 | `DSeparationQuery`, `DisjointSets`, `dsep_complete_of_query`, `dSeparated_of_dSeparated_disjoint`                                      | Pairwise-disjoint `X`, `Y`, `Z`; endpoint caveat handled; soundness direction uses `DisjointSets` explicitly |
| Markov blanket generation and semantic CI bridge                         | `MarkovGenerator`           | `computeMarkovBlanket`, `FactorizesOverDAG`, `factorizes_dsep_implies_cond_indep`, `condMarkov_of_factorizes_dsep_fourVar`             | Fully mechanized (semantic bridge; Verma-Pearl structural derivation open)                                   |
| Active collider membership (`x ∈ Anc(X∪Y∪Z)` from ¬Disjoint)             | `DAGParser`                 | `collider_mem_ancestralSubgraphNodes_of_active`                                                                                        | Fully mechanized                                                                                             |
| MAGWalk ↔ dSeparationGraph reachability                                  | `DAGParser`                 | `magWalk_iff_dSeparationGraph_reachable`                                                                                               | Fully mechanized                                                                                             |
| MAGWalk jump for active collider u → x ← w                               | `DAGParser`                 | `MAGWalk.jump_of_active_collider`                                                                                                      | Fully mechanized                                                                                             |
| Active trail → Bayes-ball state path/reachability                        | `DAGParser`                 | `bayesBallPath_of_active_trail`, `bayesBallReachable_of_active_trail`                                                                  | Fully mechanized; first-step openness is explicit                                                            |
| Active trail → moralized-graph reachability                              | `DAGParser`                 | `bayesBallPathCert_of_active_trail_outOf`, `dSeparationGraph_reachable_of_active_trail_disjoint`, `dsep_complete_of_endpoint_disjoint` | Fully mechanized under `Disjoint X Z` and `Disjoint Y Z`                                                     |
| Bayes-ball path scanner → MAGWalk                                        | `DAGParser`                 | `BayesBallPath.compress`, `MAGWalk.single_of_bayesBallStep`, `MAGWalk.jump_of_bayesBall_collider`                                      | Fully mechanized                                                                                             |
| DAG leaf deletion descent scaffold                                       | `DAGParser`                 | `DAG.deleteLeaf`, `DAG.deleteLeaf_card_lt`                                                                                             | Fully mechanized                                                                                             |
| Trail pred. ≠ moralized-ancestral pred. (counterexample)                 | `DAGParser`                 | `not_forall_dsep_iff`, `dsep_complete_endpoint_in_Z_counterexample`                                                                    | Proved: the naive equivalence is false when an endpoint is conditioned on                                    |


## Module Map

### Information-Theoretic Core

- **`FiniteQuerySandbox/InfoTheory/`** — Modularized core library:
  - `Basic.lean`: `FinitePMF` definition, Shannon summand.
  - `Entropy.lean`: Shannon entropy (bits), cardinality bounds.
  - `Marginal.lean`: Marginalization, leaf-marginalization helpers `marginalizeLeafPMF`.
  - `MutualInfo.lean`: Mutual information and its properties.
  - `Conditional.lean`: Conditional entropy, conditional mutual information, `condMarkov`.
  - `DPI.lean`: Conditional DPI (`cond_dpi`) and data processing inequalities.
  - `KL.lean`: Finite KL divergence and nonnegativity.

- **`FiniteQuerySandbox/InfoTheoryHelpers.lean`** — `IsMarkovChain`, chain rule identities,
  `cond_mutual_info_zero_of_markov`, `data_processing_inequality`.

- **`FiniteQuerySandbox/CMI_Nonneg.lean`** — Bridges `condMutualInfo_nonneg` for unconditional CMI.

### Cut-Set Bound Pipeline

- **`CutSetBoundExtract.lean`** — `pmf_from_vars` pushforward, marginal equivalence
  lemmas, `cut_set_dpi_bound` (DPI bottleneck), `abstract_cut_set_bound`
  (final inequality chain), `prop1_static_ub_from_cut`.

- **`FiniteQuerySandbox/ChannelCapacity.lean`** — `KKT_Certificate` structure (p_star, per-symbol
  bounds, KKT condition), `capacity_le_of_kkt` (weighted-average bound from KKT).

- **`FiniteQuerySandbox/CaseStudy.lean`** — Linear chain S→Y→M (State=CutVar=Missing=`Fin 2`,
  VisibleTrace=`Unit`).  `linear_chain_cut_set_bound` composes through
  `KKT_Certificate` → `abstract_cut_set_bound` → `I(S;M|T̃) ≤ 1`.
  `linear_chain_cut_set_bound_from_dag` is the alternate entry point routing
  through the DAG interface (`FactorizesOverDAG` + `dSeparates {0} {2} {1,3}`
  → `condMarkov_of_factorizes_dsep_fourVar`).

### Certificate Reductions

- **`FiniteQuerySandbox/DualCertificate.lean`** — Static (`prop1_static_ub`, `prop1_static_ub_bounded`)
  and dynamic (`prop2_dynamic_lb`, `aggregated_dynamic_lb`) certificate theorems,
  entropy decomposition, `H_S_cond_Ttilde` / `I_S_M_cond_Ttilde` definitions.

- **`FiniteQuerySandbox/DAG/`** — Modularized DAG automation:
  - `Basic.lean`: `structure DAG`, `HasEdge`, leaf nodes, topological rank.
  - `Ancestry.lean`: `ancestors`, `descendants`, `ancestralSubgraph`.
  - `Moralization.lean`: `moralGraph`, co-parent moralization edges.
  - `Trail.lean`: `inductive Trail`, trail-blocking `TripleBlocked`, `isBlocked`.
  - `BayesBall.lean`: `BayesBallStep`, `BayesBallPath`, `BayesBallReachable`.
  - `DSeparation.lean`: `dSeparated` (moralization criterion), `dSeparates` (trail predicate), `MAGWalk` bridge, and the soundness theorem `dSeparated_of_dSeparated_disjoint`.

- **`FiniteQuerySandbox/DAGParser.lean`** — Root import for the `DAG/` module suite.

- **`FiniteQuerySandbox/MarkovGenerator.lean`** — `computeMarkovBlanket`, `spouses`,
  `generateMarkovConditions`, `generateMarkovBlanketConditions`,
  `FactorizesOverDAG`, `factorizes_dsep_implies_cond_indep`,
  `condMarkovNodeCI`, `condMarkov_of_factorizes_dsep_fourVar`.

- **`FiniteQuerySandbox/DSepCMIBridge.lean`** — Bridge module between d-separation
  and conditional mutual information (CMI) for 3-variable tuple layouts.

- **`FiniteQuerySandbox/IdentifiabilityGap.lean`** — Axiom-free construction of two behaviorally
  equivalent but audit-inequivalent finite PMFs.

- **`FiniteQuerySandbox/TraceRecoverability.lean`**, **`FiniteQuerySandbox/TraceRecoverabilityBridge.lean`** —
  Deterministic trace-recoverability core and compatibility theorem.

### Impossibility Cores (Archive)

- **`FiniteQuerySandbox/FiniteQueryDecisionImpossibility.lean`**, **`FiniteQuerySandbox/PredictabilityRouteImpossibility.lean`**,
  **`FiniteQuerySandbox/SeparatedPackingImpossibility.lean`** — Finite-query, predictability-route,
  and geometric non-covering impossibility arguments.

### Auxiliary

- **`FiniteQuerySandbox/CoveringBound.lean`**, **`FiniteQuerySandbox/GeometricTools.lean`**, **`FiniteQuerySandbox/PACBounds.lean`** —
  Covering-to-gap lemmas, representation geometry, PAC algebraic core.

- **`FiniteQuerySandbox/QuotientFactorization.lean`** — Semantic-closure quotient factorization.

- **`FiniteQuerySandbox/Tools.lean`**, **`FiniteQuerySandbox/QuantizedBound.lean`** — Shared utilities.


## Architecture Overview

The verification pipeline has four layers, all implemented with zero sorries:

```
             ┌─────────────────────────────────────┐
  DAG/Markov │ DAG/* + MarkovGenerator             │  ← mechanized bridge pieces
  automation │ (d-separation, Bayes-ball, MAGWalk,  │
             │  moralization, leaf deletion,        │
             │  FactorizesOverDAG, condMarkov bridge)│
             └─────────────────────────────────────┘
                         ↓ condMarkov_of_factorizes_dsep_fourVar
             ┌─────────────────────────────────────┐
  Cut-set    │ pmf_from_vars → cut_set_dpi_bound    │  ← complete
  bound      │ → abstract_cut_set_bound             │
             └─────────────────────────────────────┘
                         ↓ h_cap : I_YZ_W(P4) ≤ C
             ┌─────────────────────────────────────┐
  KKT cert   │ KKT_Certificate → capacity_le_of_kkt │  ← complete
             │ (weighted average)                   │
             └─────────────────────────────────────┘
                         ↓ end-to-end
             ┌─────────────────────────────────────┐
  Case study │ linear_chain_cut_set_bound           │  ← complete
             │ linear_chain_cut_set_bound_from_dag  │
             └─────────────────────────────────────┘
```

`condMarkov` is verified directly on the pushforward PMF in the original
case-study theorem.  `linear_chain_cut_set_bound_from_dag` is the alternate
entry point routing through the DAG interface: `FactorizesOverDAG` plus a
`dSeparates {0} {2} {1,3}` proof supplies the concrete four-variable
`condMarkov` premise via `condMarkov_of_factorizes_dsep_fourVar`.

**Note on the two d-separation predicates.** `dSeparates` is the trail-blocking
predicate (quantifies over `Trail`s); `DAG.dSeparated` is the moralized
ancestral graph criterion (connectedness in `dSeparationGraph`).  These are
*not* generally equivalent: `not_forall_dsep_iff` and
`dsep_complete_endpoint_in_Z_counterexample` give a concrete refutation — on
the chain `0→1→2` with `Z={0}`, the moralized criterion treats endpoint 0 as
deleted, while the trail predicate still allows the one-edge trail `0→1` which
has no internal triple to block.  The two predicates coexist for different
proof purposes; the open goal is deriving `FactorizesOverDAG` from DAG
structure alone rather than assuming it per caller.

**Bayes-ball bridge status.** Active trails now compile into Bayes-ball state
paths via `bayesBallPath_of_active_trail` and into reflexive-transitive
reachability via `bayesBallReachable_of_active_trail`; the first edge is guarded
by `Trail.StartOpen` because trail blocking only constrains internal triples.
`BayesBallPath.compress` scans explicit paths with a two-step window: ordinary
windows become `MAGWalk.single`, while active-collider windows
`(a, _) → (b, into) → (c, outOf)` become one `MAGWalk.jump`, so the collider
`b` need not survive deletion of `Z`.  The bridge now derives the scanner's
`BayesBallPath.RequiredState` membership obligations from active-trail and
endpoint-disjointness hypotheses, then composes the result with
`MAGWalk.to_dSeparationGraph_reachable`.

This `MAGWalk` is currently a graph-level certificate object: it records the
large-step walk in the moralized ancestral graph.  The POPL27 sheaf story should
treat any probability/sheaf-carrying version as a separate enriched structure
(for example `SheafMAGWalk`) that projects down to this checked graph-level
`MAGWalk`.

## External Premises

The artifact leaves the following as explicit assumptions (consistent with
`sec:external-axioms` in the paper):

- **Cut-set/information-flow inequality** — premise of `prop1_static_ub` and
  `abstract_cut_set_bound`; discharged for the linear chain instance by the
  KKT certificate pipeline via `capacity_le_of_kkt`.
- **Conditional Markovity** — `condMarkov` is a concrete algebraic predicate
  on finite PMFs, not an axiom.  It is verified directly in the original case
  study; `linear_chain_cut_set_bound_from_dag` derives it via
  `FactorizesOverDAG + dSeparates`.  The open step (Stages 1–2 in the paper)
  is deriving `FactorizesOverDAG` itself from a DAG factorization theorem
  rather than supplying it as a caller hypothesis.
- **Statistical Fano and Gaussian-KL derivations** — PAC lower-bound narrative
  in the paper; not formalized.

All other information-theoretic claims (chain rule, DPI, entropy nonnegativity,
CMI nonnegativity) are proved from Mathlib first principles over finite-discrete
`FinitePMF` definitions.

## Naming Guide

The following modules have been renamed for clarity. For backward compatibility with the paper's terminology, the legacy names are retained as alias modules that import the new names.

| Legacy name | Current name |
|---|---|
| `Screenability` | `TraceRecoverability` |
| `ScreenabilityBridge` | `TraceRecoverabilityBridge` |
| `SemanticClosureIff` | `QuotientFactorization` |
| `Impossibility` | `FiniteQueryDecisionImpossibility` |
| `InternalImpossibility` | `PredictabilityRouteImpossibility` |
| `GeometricImpossibility` | `SeparatedPackingImpossibility` |

The root package namespace `FiniteQuerySandbox` is retained. `FiniteQueryAudit` is a compatibility root name.


## Open Mathematical Goals

The current artifact remains zero-sorry and `lake build` green.  The remaining
goals are mathematical or bridge-completion tasks rather than unchecked axioms:

| Goal | Where it would live | Status |
|---|---|---|
| Verma-Pearl global Markov theorem — derive `FactorizesOverDAG` from DAG structure and a product-form factorization premise | `MarkovGenerator.lean` | Open; leaf-marginalization helpers (`marginalizeLeafPMF`, `sum_leaf_pmf_eq_subgraph_pmf`) are in place |
| Full active-trail → moralized-graph bridge | `DAG/DSeparation.lean` | Mechanized for the endpoint-disjoint completeness direction via `dsep_complete_of_endpoint_disjoint`; top-level soundness theorem `dSeparated_of_dSeparated_disjoint` now takes `DisjointSets` explicitly |
| Certified decision procedure for d-separation (BFS/DFS on `dSeparationGraph`) | `DAG/DSeparation.lean` | Open |
| Blahut-Arimoto convergence and KKT concave sufficiency metatheorem | `ChannelCapacity.lean` | Open; the `KKT_Certificate` structure is in place for concrete instances |
| Trail pred. ↔ moralized-ancestral pred. equivalence | `DAG/DSeparation.lean` | **Refuted as stated** — `not_forall_dsep_iff` gives a counterexample; the endpoint-disjoint soundness direction (`dSeparated_of_dSeparated_disjoint` with `DisjointSets`) is mechanized, and the moral-path-to-active-trail direction remains the final bridge |
