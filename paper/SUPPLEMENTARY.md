# Supplementary Material — Dual Certificates for Agent Audit

This archive contains code, data, precomputed results, and the Lean 4 formalization artifact.

## Contents

```
experiments/                     # Experiment pipelines (§6.1–§6.2, Appendix B, Appendix E)
  7.1_static_certificate/        # Static certificate (min-cut, logging ablation)
  7.2_dynamic_certificate/       # Dynamic certificate (proxy/infonce/mine)
  7.3_intervention/              # Intervention & replay certificates
  7.4_synthetic_gt/              # Synthetic ground-truth validation
  README.md                      # Reproducibility guide

data/
  tool_selection/                # Tool-selection queries (600 per class, 5 classes)
  processed/                     # Precomputed result JSONs (Tables 1–4)

verification/                    # Lean 4 formalization
  FiniteQuerySandbox/
    InfoTheory.lean              # Finite PMF, entropy, conditional DPI (4 axioms declared)
    DualCertificate.lean         # Proposition 1 (cut-sum) + Proposition 2 (conditional DPI)
    Screenability.lean           # Corollary 5: autoregressive zero-cut (fully mechanized)
    ScreenabilityBridge.lean     # Bridge: EIS impossibility → zero-cut
    Tools.lean                   # List/set utilities
  lakefile.lean
  README.md
  LEAN_VERIFICATION.md
```

## Reproducibility

Setup:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch transformers scikit-learn pyyaml matplotlib numpy
```

Follow `experiments/README.md` for step-by-step reproduction. All experiments run on Apple M4 Max with Qwen2.5-7B-Instruct.

## Precomputed Results

| File | Paper Reference |
|------|----------------|
| `data/processed/logging_ablation_extracted.json` | Table 1 (static certificate: 16,464 → 0 bits) |
| `data/processed/proxy_ablation.json` | Table 2 top (proxy resolution ablation) |
| `data/processed/proxy_dormant_active.json` | Table 2 bottom (dormant/active split) |
| `data/processed/intervention/intervention_calculator_only.json` | Table 3 (dormant: JS = 0) |
| `data/processed/intervention/intervention_planning_search.json` | Table 3 (active: JS > 0) |
| `data/processed/intervention/replay_certificate.json` | Table 4 (replay certificate) |

ReAct intervention reruns also write per-sample tool distributions to
`data/processed/intervention/raw/intervention_*_samples.jsonl`. Rebuild the
aggregate JSON/CSV from those rows with
`experiments/7.3_intervention/recompute_intervention_summary.py`; aggregate
files mark the raw paths as `regenerate_required` when the rows are absent.

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

VisibleTrace=`Unit`). `linear_chain_cut_set_bound` composes through

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

DAG/Markov │ DAG/* + MarkovGenerator │ ← mechanized bridge pieces

automation │ (d-separation, Bayes-ball, MAGWalk, │

│ moralization, leaf deletion, │

│ FactorizesOverDAG, condMarkov bridge)│

└─────────────────────────────────────┘

↓ condMarkov_of_factorizes_dsep_fourVar

┌─────────────────────────────────────┐

Cut-set │ pmf_from_vars → cut_set_dpi_bound │ ← complete

bound │ → abstract_cut_set_bound │

└─────────────────────────────────────┘

↓ h_cap : I_YZ_W(P4) ≤ C

┌─────────────────────────────────────┐

KKT cert │ KKT_Certificate → capacity_le_of_kkt │ ← complete

│ (weighted average) │

└─────────────────────────────────────┘

↓ end-to-end

┌─────────────────────────────────────┐

Case study │ linear_chain_cut_set_bound │ ← complete

│ linear_chain_cut_set_bound_from_dag │

└─────────────────────────────────────┘

```

  

`condMarkov` is verified directly on the pushforward PMF in the original

case-study theorem. `linear_chain_cut_set_bound_from_dag` is the alternate

entry point routing through the DAG interface: `FactorizesOverDAG` plus a

`dSeparates {0} {2} {1,3}` proof supplies the concrete four-variable

`condMarkov` premise via `condMarkov_of_factorizes_dsep_fourVar`.

  

**Note on the two d-separation predicates.** `dSeparates` is the trail-blocking

predicate (quantifies over `Trail`s); `DAG.dSeparated` is the moralized

ancestral graph criterion (connectedness in `dSeparationGraph`). These are

*not* generally equivalent: `not_forall_dsep_iff` and

`dsep_complete_endpoint_in_Z_counterexample` give a concrete refutation — on

the chain `0→1→2` with `Z={0}`, the moralized criterion treats endpoint 0 as

deleted, while the trail predicate still allows the one-edge trail `0→1` which

has no internal triple to block. The two predicates coexist for different

proof purposes; the open goal is deriving `FactorizesOverDAG` from DAG

structure alone rather than assuming it per caller.

  

**Bayes-ball bridge status.** Active trails now compile into Bayes-ball state

paths via `bayesBallPath_of_active_trail` and into reflexive-transitive

reachability via `bayesBallReachable_of_active_trail`; the first edge is guarded

by `Trail.StartOpen` because trail blocking only constrains internal triples.

`BayesBallPath.compress` scans explicit paths with a two-step window: ordinary

windows become `MAGWalk.single`, while active-collider windows

`(a, _) → (b, into) → (c, outOf)` become one `MAGWalk.jump`, so the collider

`b` need not survive deletion of `Z`. The bridge now derives the scanner's

`BayesBallPath.RequiredState` membership obligations from active-trail and

endpoint-disjointness hypotheses, then composes the result with

`MAGWalk.to_dSeparationGraph_reachable`.

  

This `MAGWalk` is currently a graph-level certificate object: it records the

large-step walk in the moralized ancestral graph. The POPL27 sheaf story should

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

on finite PMFs, not an axiom. It is verified directly in the original case

study; `linear_chain_cut_set_bound_from_dag` derives it via

`FactorizesOverDAG + dSeparates`. The open step (Stages 1–2 in the paper)

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

  

The current artifact remains zero-sorry and `lake build` green. The remaining goals are mathematical or bridge-completion tasks rather than unchecked axioms:

| Goal | Where it would live | Status |

|---|---|---|

| Verma-Pearl global Markov theorem — derive `FactorizesOverDAG` from DAG structure and a product-form factorization premise | `MarkovGenerator.lean` | Open; leaf-marginalization helpers (`marginalizeLeafPMF`, `sum_leaf_pmf_eq_subgraph_pmf`) are in place |

| Full active-trail → moralized-graph bridge | `DAG/DSeparation.lean` | Mechanized for the endpoint-disjoint completeness direction via `dsep_complete_of_endpoint_disjoint`; top-level soundness theorem `dSeparated_of_dSeparated_disjoint` now takes `DisjointSets` explicitly |

| Certified decision procedure for d-separation (BFS/DFS on `dSeparationGraph`) | `DAG/DSeparation.lean` | Open |

| Blahut-Arimoto convergence and KKT concave sufficiency metatheorem | `ChannelCapacity.lean` | Open; the `KKT_Certificate` structure is in place for concrete instances |

| Trail pred. ↔ moralized-ancestral pred. equivalence | `DAG/DSeparation.lean` | **Refuted as stated** — `not_forall_dsep_iff` gives a counterexample; the endpoint-disjoint soundness direction (`dSeparated_of_dSeparated_disjoint` with `DisjointSets`) is mechanized, and the moral-path-to-active-trail direction remains the final bridge |
