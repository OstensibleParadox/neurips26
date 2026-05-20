import FiniteQuerySandbox.InfoTheory.Basic

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

/-! ### Marginal definitions and lemmas -/

def marginalLeftMass (P : FinitePMF (α × β)) (x : α) : ℝ :=
  ∑ y : β, P.pmf (x, y)

def marginalRightMass (P : FinitePMF (α × β)) (y : β) : ℝ :=
  ∑ x : α, P.pmf (x, y)

lemma marginalLeftMass_nonneg (P : FinitePMF (α × β)) (x : α) :
    0 ≤ marginalLeftMass P x :=
  Finset.sum_nonneg (fun y _ => P.pmf_nonneg (x, y))

lemma marginalRightMass_nonneg (P : FinitePMF (α × β)) (y : β) :
    0 ≤ marginalRightMass P y :=
  Finset.sum_nonneg (fun x _ => P.pmf_nonneg (x, y))

lemma marginalLeftMass_sum_one (P : FinitePMF (α × β)) :
    ∑ x : α, marginalLeftMass P x = 1 := by
  unfold marginalLeftMass
  rw [← Fintype.sum_prod_type]
  exact P.sum_one

lemma marginalRightMass_sum_one (P : FinitePMF (α × β)) :
    ∑ y : β, marginalRightMass P y = 1 := by
  unfold marginalRightMass
  rw [Finset.sum_comm]
  rw [← Fintype.sum_prod_type]
  exact P.sum_one

/--
Marginalize a leaf coordinate from a product-state PMF.  In the DAG proof this
is the PMF on the remaining subgraph after summing out a leaf variable.
-/
def marginalizeLeafPMF (P : FinitePMF (α × β)) : FinitePMF α where
  pmf x := ∑ leaf : β, P.pmf (x, leaf)
  pmf_nonneg x := by
    exact Finset.sum_nonneg fun leaf _ => P.pmf_nonneg (x, leaf)
  sum_one := by
    calc
      ∑ x : α, ∑ leaf : β, P.pmf (x, leaf)
          = ∑ p : α × β, P.pmf p := by
            rw [← Fintype.sum_prod_type]
      _ = 1 := P.sum_one

/--
Helper lemma for the leaf-marginalization step in the DAG Markov proof:
the subgraph PMF at a remaining assignment is exactly the sum of the original
joint PMF over the leaf coordinate.
-/
lemma sum_leaf_pmf_eq_subgraph_pmf (P : FinitePMF (α × β)) (x : α) :
    (∑ leaf : β, P.pmf (x, leaf)) = (marginalizeLeafPMF P).pmf x := by
  rfl

lemma marginalLeftMass_le_one (P : FinitePMF (α × β)) (x : α) :
    marginalLeftMass P x ≤ 1 := by
  have h_nonneg : ∀ x, 0 ≤ marginalLeftMass P x := marginalLeftMass_nonneg P
  have : marginalLeftMass P x ≤ ∑ x : α, marginalLeftMass P x :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ x)
  linarith [marginalLeftMass_sum_one P]

lemma marginalRightMass_le_one (P : FinitePMF (α × β)) (y : β) :
    marginalRightMass P y ≤ 1 := by
  have h_nonneg : ∀ y, 0 ≤ marginalRightMass P y := marginalRightMass_nonneg P
  have : marginalRightMass P y ≤ ∑ y : β, marginalRightMass P y :=
    Finset.single_le_sum (fun y' _ => h_nonneg y') (Finset.mem_univ y)
  linarith [marginalRightMass_sum_one P]

lemma pmf_le_marginalLeftMass (P : FinitePMF (α × β)) (x : α) (y : β) :
    P.pmf (x, y) ≤ marginalLeftMass P x := by
  unfold marginalLeftMass
  exact Finset.single_le_sum (fun y' _ => P.pmf_nonneg (x, y')) (Finset.mem_univ y)

lemma pmf_le_marginalRightMass (P : FinitePMF (α × β)) (x : α) (y : β) :
    P.pmf (x, y) ≤ marginalRightMass P y := by
  unfold marginalRightMass
  exact Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', y)) (Finset.mem_univ x)

end

end FiniteQuerySandbox
