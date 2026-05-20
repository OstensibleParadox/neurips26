import FiniteQuerySandbox.DAGParser
import FiniteQuerySandbox.InfoTheory

open Finset

namespace FiniteQuerySandbox

noncomputable section

/-!
# Markov Generator

This module contains the combinatorial Markov-condition generator that sits on
top of `DAGParser`.  The full Verma-Pearl global Markov theorem is not proved
here; instead, `FactorizesOverDAG` is a semantic package saying that the chosen
probability model validates every conditional independence licensed by
d-separation.  The bridge theorem then exposes the exact proof term downstream
code needs.
-/

/-- Parents of children other than the node itself. -/
def spouses (G : DAG) (v : ℕ) : Finset ℕ :=
  ((children G v).biUnion fun c => parents G c) \ {v}

/-- The DAG Markov blanket `Pa(v) ∪ Ch(v) ∪ Pa(Ch(v)) \ {v}`. -/
def computeMarkovBlanket (G : DAG) (v : ℕ) : Finset ℕ :=
  parents G v ∪ children G v ∪ spouses G v

/--
Generated local Markov conditions:
`({v}, nonDescendants(v) \ parents(v), parents(v))`.
-/
def generateMarkovConditions (G : DAG) : List (Finset ℕ × Finset ℕ × Finset ℕ) :=
  G.nodes.toList.map fun v => ({v}, nonDescendants G v \ parents G v, parents G v)

/--
Generated blanket conditions:
`({v}, nodes \ ({v} ∪ MB(v)), MB(v))`.
-/
def generateMarkovBlanketConditions (G : DAG) : List (Finset ℕ × Finset ℕ × Finset ℕ) :=
  G.nodes.toList.map fun v => ({v}, G.nodes \ ({v} ∪ computeMarkovBlanket G v),
    computeMarkovBlanket G v)

/--
A model-specific conditional-independence predicate over node sets.  The PMF
state space is left abstract because this project currently uses concrete tuple
types for probability statements (`condMarkov`, `IsMarkovChain`) rather than a
generic finite-assignment API.
-/
abbrev CondIndepPredicate (Ω : Type) [Fintype Ω] [DecidableEq Ω] :=
  FinitePMF Ω → Finset ℕ → Finset ℕ → Finset ℕ → Prop

/--
Semantic DAG factorization package: every d-separation statement in `G` is
valid as a conditional-independence statement for `P`.
-/
def FactorizesOverDAG {Ω : Type} [Fintype Ω] [DecidableEq Ω]
    (G : DAG) (CI : CondIndepPredicate Ω) (P : FinitePMF Ω) : Prop :=
  ∀ X Y Z : Finset ℕ, dSeparates G X Y Z → CI P X Y Z

/--
The soundness bridge used by downstream automation.  It is deliberately stated
against `FactorizesOverDAG`, not as the full Verma-Pearl theorem, so the kernel
only accepts conditional independences explicitly supplied by the model
semantics.
-/
theorem factorizes_dsep_implies_cond_indep {Ω : Type} [Fintype Ω] [DecidableEq Ω]
    (G : DAG) (CI : CondIndepPredicate Ω) (P : FinitePMF Ω)
    (X Y Z : Finset ℕ)
    (h_factor : FactorizesOverDAG G CI P)
    (h_dsep : dSeparates G X Y Z) :
    CI P X Y Z :=
  h_factor X Y Z h_dsep

/--
Adapter from node-set conditional independence to the existing concrete
four-variable `condMarkov` equality.  Node labels follow the tuple order:
`0 = X`, `1 = Y`, `2 = Z`, `3 = W`; hence the relevant CI is
`{0} ⟂ {2} | {1, 3}`.
-/
def condMarkovNodeCI {α β γ δ : Type}
    [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P : FinitePMF (α × β × γ × δ))
    (X Z YW : Finset ℕ) : Prop :=
  X = ({0} : Finset ℕ) →
    Z = ({2} : Finset ℕ) →
    YW = ({1, 3} : Finset ℕ) →
    condMarkov P

/--
Extract the concrete `condMarkov` hypothesis required by the existing DPI layer
from a semantic DAG factorization package and a d-separation proof for the
four-variable tuple layout.
-/
theorem condMarkov_of_factorizes_dsep_fourVar {α β γ δ : Type}
    [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (G : DAG) (P : FinitePMF (α × β × γ × δ))
    (h_factor : FactorizesOverDAG G condMarkovNodeCI P)
    (h_dsep : dSeparates G ({0} : Finset ℕ) ({2} : Finset ℕ) ({1, 3} : Finset ℕ)) :
    condMarkov P :=
  h_factor ({0} : Finset ℕ) ({2} : Finset ℕ) ({1, 3} : Finset ℕ) h_dsep rfl rfl rfl

namespace MarkovGeneratorExamples

open DAGExamples

example : computeMarkovBlanket chain3 1 = ({0, 2} : Finset ℕ) := by
  decide

example : computeMarkovBlanket collider3 0 = ({1, 2} : Finset ℕ) := by
  decide

end MarkovGeneratorExamples

end

end FiniteQuerySandbox
