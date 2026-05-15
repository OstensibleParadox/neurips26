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
| Identifiability gap (Thm 1) | `IdentifiabilityGap` | `identifiability_gap_extremes` | Fully mechanized |
| Static certificate reduction (Prop 1) | `DualCertificate` | `prop1_static_ub` | From cut-set premise |
| Dynamic certificate reduction (Prop 2) | `DualCertificate` | `prop2_dynamic_lb` | From finite DPI |
| Autoregressive zero-cut (Cor 2) | `Screenability` | `no_eis_autoregressive` | Fully mechanized |
| Static cardinality corollary | `DualCertificate` | `prop1_static_ub_bounded` | Fully mechanized |
| Deterministic trace recoverability | `TraceRecoverability` | `no_internal_witness_trace_recoverability` | Fully mechanized |
| KKT certificate capacity bound | `ChannelCapacity` | `capacity_le_of_kkt` | From per-symbol KKT condition |
| Linear chain cut-set bound | `CaseStudy` | `linear_chain_cut_set_bound` | KKT cert + DPI + `abstract_cut_set_bound` |

## Module Map

### Information-Theoretic Core

- **`InfoTheory.lean`** — `FinitePMF`, Shannon entropy (bits), conditional entropy,
  mutual information, conditional mutual information, finite KL nonnegativity,
  entropy cardinality bound, `condMarkov` factorization, conditional DPI
  (`cond_dpi` proved from first principles).

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
             ┌─────────────────────────────┐
  DAG/Markov │ DAGParser + MarkovGenerator  │  ← follow-up paper
  automation │ (d-separation, blanket,      │     (not yet implemented)
  (§1–2 in   │  FactorizesOverDAG)          │
   details)  │                              │
             └─────────────────────────────┘
                         ↓ condMarkov
             ┌─────────────────────────────┐
  Cut-set    │ pmf_from_vars → cut_set_dpi  │  ← abstract_cut_set_bound
  bound      │ _bound → abstract_cut_set_   │     (implemented)
  (§3 in     │ bound                        │
   details)  │                              │
             └─────────────────────────────┘
                         ↓ h_cap : I_YZ_W(P4) ≤ C
             ┌─────────────────────────────┐
  KKT cert   │ KKT_Certificate → capacity_  │  ← ChannelCapacity.lean
  (§4.2 in   │ le_of_kkt (weighted average) │     (implemented)
   details)  │                              │
             └─────────────────────────────┘
```

Detailed proof methods for each layer—DAG local Markov property,
Markov blanket computation, d-separation algorithm, Blahut-Arimoto
iteration, KKT sufficient condition—are documented in
[`dag_markov_details.md`](./dag_markov_details.md), with per-section
implementation status annotations.

For the linear chain case study, `condMarkov` is verified directly on the
pushforward PMF; the DAG automation stages (d-separation, Markov blanket
computation) are deferred to a follow-up paper.

## External Premises

The artifact leaves the following as explicit assumptions:

- **cut-set/information-flow inequality** — premise of `prop1_static_ub`;
  the `ChannelCapacity` module provides a KKT-certificate verification path for
  concrete instances.
- **conditional Markovity** — structural modeling premise (`condMarkov` is
  defined algebraically and verified directly in the case study; the DAG→condMarkov
  automation is future work).
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
(detailed proof methods in [`dag_markov_details.md`](./dag_markov_details.md)):

| Stage | Module | Status | Target |
|---|---|---|---|
| 1 — DAG 谓词语义与拓扑序 | `DAGParser.lean` | ❌ Not started | DAG structure, WellFounded acyclicity, topological sort, set queries |
| 2 — 马尔可夫语义桥接与自动化 | `MarkovGenerator.lean` | ❌ Not started | FactorizesOverDAG, Markov blanket, d-separation, soundness theorem |
| 3 — 信道容量与 KKT 证书核验 | `ChannelCapacity.lean` | ✅ Completed | KKT_Certificate + capacity_le_of_kkt (BA iteration not formalized) |
| 4 — 线性链端到端验证 | `CaseStudy.lean` | ✅ Completed | Linear chain S→Y→M → abstract_cut_set_bound |

Stages 1–2 form the core of a planned follow-up paper
*"Topology-to-Certificate: A Verified Pipeline from DAG Structure to
Information-Theoretic Audit Bounds"* (target: PLDI/POPL/CAV or NeurIPS
theory track).  Stage 3's KKT framework is structurally ready for non-trivial
certificates; the full Blahut-Arimoto convergence proof and concave KKT
sufficiency metatheorem are deferred to the same follow-up.
