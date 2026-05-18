# Plan: DAGParser + MarkovGenerator (Stages 1-2)

## Context

Stages 3-4 (ChannelCapacity, CaseStudy) are complete. The linear chain
case study works, but `condMarkov` is provided as a hypothesis — a human
read the graph, computed the Markov blanket, and hand-coded the independence
conditions. Stages 1-2 replace that manual step with an automated pipeline:
DAG structure → d-separation → conditional independence declarations →
`condMarkov`.

**Current implementation update.** The first Lean pass now includes finite DAG
infrastructure, `IsLeaf` and `exists_leaf_of_nonempty`, parent/child/
ancestor/descendant queries, trail-blocking `dSeparates`, the ancestral
subgraph/moralization/deletion/connectedness predicate `DAG.dSeparated`, Markov
blanket generation, and the four-variable `condMarkov` adapter. `InfoTheory`
also contains `marginalizeLeafPMF` and `sum_leaf_pmf_eq_subgraph_pmf` for the
leaf-elimination step. Still pending: trail↔moralization equivalence,
certified decision procedures, and the full Verma-Pearl global Markov theorem.

## What Already Exists (landscape scan)

### Mathlib

- **`Digraph V`**: `Adj : V → V → Prop` with lattice operations. Bare — no
  walks, paths, acyclicity, or topological ordering. Not usable as-is.
- **`SimpleGraph.Walk`**: Comprehensive undirected walk/path/types. Directed
  analogue does not exist.
- **`Relation.ReflTransGen`**: Reflexive transitive closure of any relation.
  Correct primitive for directed reachability: `ancestors(v) = { u | ReflTransGen G.Adj u v }`.
- **`Quiver.Path`**: Typed directed path type, but too heavy — uses
  `Hom : V → V → Type` rather than Prop-valued edges.

### Our codebase (`FiniteQuerySandbox/`)

- **`FinitePMF`**: custom discrete PMF with `[Fintype α] [DecidableEq α]`
- **`condMarkov`**: 4-variable multiplicative equality: `P(x,y,z,w) * P(y,w) = P(x,y,w) * P(y,z,w)`
- **`IsMarkovChain`**: 3-variable version: `P(a,b,c) * P(b) = P(a,b) * P(b,c)`
- **Naming conventions**: `marginal<Var>Mass`, `entropyOf`, `_nonneg`, `_sum_one`
- **DAG graph layer** now exists in `DAGParser.lean`

### Unique (no Lean precedent found)

- No DAG formalization with d-separation exists in any Lean package
- No Verma-Pearl soundness theorem formalized in Lean, Coq, or Isabelle

## Goal

Produce and connect 2 Lean files:

1. **`DAGParser.lean`** — Directed Acyclic Graph infrastructure: structure
   definition, acyclicity via `WellFounded`, reachability via
   `Relation.ReflTransGen`, descendant/ancestor sets, topological ordering,
   leaf-node support, trail-based d-separation, and the moralized ancestral
   graph criterion.

2. **`MarkovGenerator.lean`** — Markov blanket computation and the
   `factorizes_dsep_implies_cond_indep` semantic bridge. This is not yet the
   full Verma-Pearl 1988 theorem; it packages model-specific CI facts behind
   `FactorizesOverDAG`.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ DAGParser.lean                                      │
│                                                     │
│ structure DAG where                                  │
│   nodes  : Finset ℕ                                 │
│   edges  : Finset (ℕ × ℕ)                           │
│   acyclic : WellFounded (λ x y => (x,y) ∈ edges)     │
│                                                     │
│ def Reachable (G : DAG) (u v : ℕ) : Prop :=          │
│   Relation.ReflTransGen (λ x y => (x,y) ∈ G.edges)  │
│                                                     │
│ def descendants (G : DAG) (v : ℕ) : Finset ℕ         │
│ def ancestors (G : DAG) (v : ℕ) : Finset ℕ           │
│ def parents (G : DAG) (v : ℕ) : Finset ℕ             │
│ def children (G : DAG) (v : ℕ) : Finset ℕ            │
│ def IsLeaf (G : DAG) (v : ℕ) : Prop                  │
│ lemma exists_leaf_of_nonempty ...                     │
│                                                     │
│ inductive Trail (G : DAG) : ℕ → ℕ → Type             │
│   forward/backward undirected trail steps             │
│                                                     │
│ def dSeparates (G : DAG) (X Y Z : Finset ℕ) : Prop   │
│ def DAG.dSeparated (G : DAG) (X Y Z : Finset ℕ) : Prop│
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│ MarkovGenerator.lean                                │
│                                                     │
│ def computeMarkovBlanket (G : DAG) (v : ℕ) :         │
│   Finset ℕ := Pa(v) ∪ Ch(v) ∪ Pa(Ch(v))             │
│                                                     │
│ def FactorizesOverDAG (G : DAG)                      │
│   (CI : CondIndepPredicate Ω) (P : FinitePMF Ω)      │
│     : Prop :=                                        │
│   ∀ X Y Z, dSeparates G X Y Z → CI P X Y Z           │
│                                                     │
│ theorem factorizes_dsep_implies_cond_indep           │
│   (G : DAG) (CI : CondIndepPredicate Ω)              │
│   (P : FinitePMF Ω)                                  │
│   (h_factor : FactorizesOverDAG G CI P)              │
│   (h_dsep : dSeparates G X Y Z) :                    │
│   CI P X Y Z := ...                                  │
│                                                     │
│ def generateMarkovConditions (G : DAG) :              │
│   List (Finset ℕ × Finset ℕ × Finset ℕ)              │
└─────────────────────────────────────────────────────┘
```

## DAGParser.lean — Detailed Design

### 1. `structure DAG`

```lean
structure DAG where
  nodes : Finset ℕ
  edges : Finset (ℕ × ℕ)
  edges_subset : edges ⊆ nodes ×ˢ nodes
  acyclic : WellFounded (λ x y => (x, y) ∈ edges)
```

- `nodes` and `edges` as `Finset ℕ` ensures finiteness, making all queries
  computable via `Finset` operations.
- `WellFounded` is the Mathlib standard for acyclicity: there is no infinite
  descending chain. This doesn't require a separate `noLoops` condition
  (loops would create `(v, v) ∈ edges`, violating `WellFounded`).
- Using `ℕ` rather than a generic type `V` keeps the first pass simple;
  generic `V` can be added later via `[Fintype V] [DecidableEq V]`.

### 2. Basic Queries

All queries are `Finset`-based and deterministic:

```lean
def parents (G : DAG) (v : ℕ) : Finset ℕ :=
  G.edges.filter (λ e => e.2 = v) |>.image Prod.fst

def children (G : DAG) (v : ℕ) : Finset ℕ :=
  G.edges.filter (λ e => e.1 = v) |>.image Prod.snd
```

Descendants and ancestors are finite filters over the node set using directed
reachability:

```lean
def descendants (G : DAG) (v : ℕ) : Finset ℕ :=
  G.nodes.filter fun w => w ≠ v ∧ Reachable G v w

def ancestors (G : DAG) (v : ℕ) : Finset ℕ :=
  G.nodes.filter fun u => u ≠ v ∧ Reachable G u v

def nonDescendants (G : DAG) (v : ℕ) : Finset ℕ :=
  G.nodes \ ({v} ∪ descendants G v)

def IsLeaf (G : DAG) (v : ℕ) : Prop :=
  v ∈ G.nodes ∧ children G v = ∅

lemma exists_leaf_of_nonempty (G : DAG) (h_nodes : G.nodes.Nonempty) :
    ∃ v : ℕ, IsLeaf G v := ...
```

### 3. Reachability

```lean
def Reachable (G : DAG) (u v : ℕ) : Prop :=
  Relation.ReflTransGen (λ x y => (x, y) ∈ G.edges) u v
```

This is a `Prop`, not a `Finset`; it includes the zero-length path. The
acyclicity condition instead rules out nonempty directed cycles
(`¬ Relation.TransGen ... v v`), which is used by the leaf-existence proof.

### 4. d-separation

The trail-based d-separation presentation is represented in two layers, but
certified trail enumeration is still pending:

**Layer 1 — Path existence**: For a given (X, Y, Z), the theorem-facing
predicate quantifies over every undirected trail between X and Y. A future
decision procedure can enumerate trails via BFS on the **undirected** version
of the finite graph.

**Layer 2 — Blocking check**: A trail is blocked by Z if it contains
either (a) a chain/fork node in Z, or (b) a collider node whose
descendants are all outside Z.

```lean
/-- A trail (undirected path) between u and v in the DAG.
    Each step is either forward (u→w) or backward (w→u). -/
inductive Trail (G : DAG) : ℕ → ℕ → Type
  | nil (v : ℕ) : Trail v v
  | forward (u w : ℕ) (h : (u, w) ∈ G.edges) (t : Trail w v) : Trail u v
  | backward (u w : ℕ) (h : (w, u) ∈ G.edges) (t : Trail w v) : Trail u v

/-- A node on a trail is a collider if it has two incoming edges on the trail. -/
def Trail.isCollider (G : DAG) (t : Trail G u v) (w : ℕ) : Prop := ...

/-- A trail is blocked by Z. -/
def Trail.isBlocked (G : DAG) (Z : Finset ℕ) (t : Trail G u v) : Prop := ...

/-- Z d-separates X and Y. -/
def dSeparates (G : DAG) (X Y Z : Finset ℕ) : Prop :=
  ∀ (x ∈ X) (y ∈ Y) (t : Trail G x y), Trail.isBlocked G Z t
```

### 5. Moralized ancestral graph criterion

This is now represented directly in Lean and should become the preferred
decision-oriented presentation after an equivalence theorem is added:

```lean
def DAG.ancestors (G : DAG) (v : ℕ) : Finset ℕ := ...
def DAG.ancestralSubgraphNodes (G : DAG) (S : Finset ℕ) : Finset ℕ := ...
def DAG.ancestralSubgraph (G : DAG) (S : Finset ℕ) : DAG := ...
def DAG.coParents (G : DAG) (u v : ℕ) : Prop := ...
def DAG.moralGraph (G : DAG) (S : Finset ℕ) : SimpleGraph ℕ := ...
def DAG.dSeparationGraph (G : DAG) (X Y Z : Finset ℕ) : SimpleGraph ℕ := ...
def DAG.dSeparated (G : DAG) (X Y Z : Finset ℕ) : Prop := ...
```

Open proof obligation: show this criterion agrees with the trail-blocking
`dSeparates` predicate, or move the semantic bridge to `DAG.dSeparated` and
prove soundness directly from the graph transformation.

## MarkovGenerator.lean — Detailed Design

### 1. Markov Blanket

Pure combinatorics — no probability:

```lean
def computeMarkovBlanket (G : DAG) (v : ℕ) : Finset ℕ :=
  let Pa := parents G v
  let Ch := children G v
  let Sp := Ch.biUnion (λ c => parents G c) \ {v}
  Pa ∪ Ch ∪ Sp
```

### 2. FactorizesOverDAG

The implemented first pass is a semantic package, not a product-form
factorization theorem. It states that every graphically permitted
d-separation fact is valid for the model-specific conditional-independence
predicate supplied by the caller:

```lean
abbrev CondIndepPredicate (Ω : Type) [Fintype Ω] [DecidableEq Ω] :=
  FinitePMF Ω → Finset ℕ → Finset ℕ → Finset ℕ → Prop

def FactorizesOverDAG (G : DAG) (CI : CondIndepPredicate Ω) (P : FinitePMF Ω) : Prop :=
  ∀ X Y Z : Finset ℕ, dSeparates G X Y Z → CI P X Y Z
```

### 3. Capstone Theorem

```lean
theorem factorizes_dsep_implies_cond_indep
    (G : DAG) (CI : CondIndepPredicate Ω) (P : FinitePMF Ω)
    (h_factor : FactorizesOverDAG G CI P)
    (X Y Z : Finset ℕ) (h_dsep : dSeparates G X Y Z) :
    CI P X Y Z := ...
```

This theorem is intentionally thin: it projects the corresponding CI fact out
of `FactorizesOverDAG`. It is the bridge used by the current case study, not
the full graph-to-probability theorem.

The future Verma-Pearl 1988 construction still needs:
1. Show that d-separation in G implies the existence of an ordering
   of nodes compatible with the DAG topology.
2. Use the factorization to decompose the joint distribution.
3. Use leaf marginalization (`sum_leaf_pmf_eq_subgraph_pmf`) to eliminate nodes
   while preserving the local Markov property.
4. Marginalize and condition to obtain the independence.

## Implementation Order

### Step 1 — `DAGParser.lean` foundation (~200 lines)
- `structure DAG`
- `parents`, `children`, `descendants`, `ancestors`, `nonDescendants`
- `Reachable` via `ReflTransGen`
- `IsLeaf`, `exists_leaf_of_nonempty`
- Tests: manually construct 3-node chains and forks, verify queries

### Step 2 — `Trail` and `dSeparates` (~250 lines)
- `inductive Trail`
- `Trail.isCollider`, `Trail.isBlocked`
- `dSeparates`
- `DAG.ancestralSubgraph`, `DAG.moralGraph`, `DAG.dSeparationGraph`,
  `DAG.dSeparated`
- Tests: chain X→Z→Y d-separated by {Z}, fork X←Z→Y d-separated by {Z},
  collider X→Z←Y NOT d-separated by ∅ but d-separated by Z's descendant

### Step 3 — `MarkovGenerator.lean` definitions (~150 lines)
- `computeMarkovBlanket`
- `FactorizesOverDAG`
- `CondIndep` definition (adapt from existing `condMarkov` pattern)

### Step 4 — Soundness theorem
- Current: `factorizes_dsep_implies_cond_indep` semantic bridge
- Future: full Verma-Pearl theorem using leaf elimination, moralization
  equivalence, and a genuine DAG factorization/local Markov premise

## Verification Plan

1. `lake build` passes with no sorries
2. Each d-separation test case compiles and can be `#check`ed
3. The 3-node chain case study from `CaseStudy.lean` can be re-derived
   via `dSeparates` + `factorizes_dsep_implies_cond_indep` instead of
   the manual `h_markov` hypothesis
4. Future check: prove or assume a bridge from `DAG.dSeparated` to
   `dSeparates`, then reroute the four-variable case through the moralized
   ancestral graph predicate
