import FiniteQuerySandbox.InfoTheory.Basic

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

/-! ### Pair marginals -/

def marginalPairFst (P : FinitePMF (α × β)) (x : α) : ℝ :=
  ∑ y : β, P.pmf (x, y)

def marginalPairSnd (P : FinitePMF (α × β)) (y : β) : ℝ :=
  ∑ x : α, P.pmf (x, y)

lemma marginalPairFst_nonneg (P : FinitePMF (α × β)) (x : α) :
    0 ≤ marginalPairFst P x :=
  Finset.sum_nonneg (fun y _ => P.pmf_nonneg (x, y))

lemma marginalPairSnd_nonneg (P : FinitePMF (α × β)) (y : β) :
    0 ≤ marginalPairSnd P y :=
  Finset.sum_nonneg (fun x _ => P.pmf_nonneg (x, y))

lemma marginalPairFst_sum_one (P : FinitePMF (α × β)) :
    ∑ x : α, marginalPairFst P x = 1 := by
  unfold marginalPairFst
  rw [← Fintype.sum_prod_type]
  exact P.sum_one

lemma marginalPairSnd_sum_one (P : FinitePMF (α × β)) :
    ∑ y : β, marginalPairSnd P y = 1 := by
  unfold marginalPairSnd
  rw [Finset.sum_comm]
  rw [← Fintype.sum_prod_type]
  exact P.sum_one

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

lemma marginalPairFst_le_one (P : FinitePMF (α × β)) (x : α) :
    marginalPairFst P x ≤ 1 := by
  have h_nonneg : ∀ x, 0 ≤ marginalPairFst P x := marginalPairFst_nonneg P
  have : marginalPairFst P x ≤ ∑ x : α, marginalPairFst P x :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ x)
  linarith [marginalPairFst_sum_one P]

lemma marginalPairSnd_le_one (P : FinitePMF (α × β)) (y : β) :
    marginalPairSnd P y ≤ 1 := by
  have h_nonneg : ∀ y, 0 ≤ marginalPairSnd P y := marginalPairSnd_nonneg P
  have : marginalPairSnd P y ≤ ∑ y : β, marginalPairSnd P y :=
    Finset.single_le_sum (fun y' _ => h_nonneg y') (Finset.mem_univ y)
  linarith [marginalPairSnd_sum_one P]

lemma pmf_le_marginalPairFst (P : FinitePMF (α × β)) (x : α) (y : β) :
    P.pmf (x, y) ≤ marginalPairFst P x := by
  unfold marginalPairFst
  exact Finset.single_le_sum (fun y' _ => P.pmf_nonneg (x, y')) (Finset.mem_univ y)

lemma pmf_le_marginalPairSnd (P : FinitePMF (α × β)) (x : α) (y : β) :
    P.pmf (x, y) ≤ marginalPairSnd P y := by
  unfold marginalPairSnd
  exact Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', y)) (Finset.mem_univ x)

/-! ## Three-variable marginals -/

def marginalTripleThd (P : FinitePMF (α × β × γ)) (z : γ) : ℝ :=
  ∑ x : α, ∑ y : β, P.pmf (x, y, z)

def marginalTripleFstThd (P : FinitePMF (α × β × γ)) (xz : α × γ) : ℝ :=
  ∑ y : β, P.pmf (xz.1, y, xz.2)

def marginalTripleSndThd (P : FinitePMF (α × β × γ)) (yz : β × γ) : ℝ :=
  ∑ x : α, P.pmf (x, yz.1, yz.2)

lemma marginalTripleFstThd_nonneg (P : FinitePMF (α × β × γ)) (xz : α × γ) :
    0 ≤ marginalTripleFstThd P xz :=
  Finset.sum_nonneg (fun y _ => P.pmf_nonneg (xz.1, y, xz.2))

lemma marginalTripleSndThd_nonneg (P : FinitePMF (α × β × γ)) (yz : β × γ) :
    0 ≤ marginalTripleSndThd P yz :=
  Finset.sum_nonneg (fun x _ => P.pmf_nonneg (x, yz.1, yz.2))

lemma marginalTripleThd_nonneg (P : FinitePMF (α × β × γ)) (z : γ) :
    0 ≤ marginalTripleThd P z :=
  Finset.sum_nonneg (fun x _ => Finset.sum_nonneg (fun y _ => P.pmf_nonneg (x, y, z)))

lemma marginalTripleFstThd_sum_thd (P : FinitePMF (α × β × γ)) (z : γ) :
    ∑ x : α, marginalTripleFstThd P (x, z) = marginalTripleThd P z := by
  rfl

lemma marginalTripleSndThd_sum_thd (P : FinitePMF (α × β × γ)) (z : γ) :
    ∑ y : β, marginalTripleSndThd P (y, z) = marginalTripleThd P z := by
  unfold marginalTripleSndThd marginalTripleThd
  rw [Finset.sum_comm]

lemma marginalTripleThd_sum_one (P : FinitePMF (α × β × γ)) :
    ∑ z : γ, marginalTripleThd P z = 1 := by
  have hsum : (∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z)) = 1 := by
    calc
      (∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z))
          = ∑ x : α, ∑ yz : β × γ, P.pmf (x, yz.1, yz.2) := by
            apply Finset.sum_congr rfl
            intro x _
            rw [← Fintype.sum_prod_type' (fun y z => P.pmf (x, y, z))]
      _ = ∑ xyz : α × β × γ, P.pmf xyz := by
            rw [← Fintype.sum_prod_type]
      _ = 1 := P.sum_one
  unfold marginalTripleThd
  rw [Finset.sum_comm]
  rw [show (∑ x : α, ∑ z : γ, ∑ y : β, P.pmf (x, y, z))
      = ∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z) by
        apply Finset.sum_congr rfl
        intro x _
        rw [Finset.sum_comm]]
  exact hsum

lemma pmf_le_marginalTripleFstThd (P : FinitePMF (α × β × γ)) (x : α) (y : β) (z : γ) :
    P.pmf (x, y, z) ≤ marginalTripleFstThd P (x, z) := by
  unfold marginalTripleFstThd
  exact Finset.single_le_sum (fun y' _ => P.pmf_nonneg (x, y', z)) (Finset.mem_univ y)

lemma pmf_le_marginalTripleSndThd (P : FinitePMF (α × β × γ)) (x : α) (y : β) (z : γ) :
    P.pmf (x, y, z) ≤ marginalTripleSndThd P (y, z) := by
  unfold marginalTripleSndThd
  exact Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', y, z)) (Finset.mem_univ x)

lemma marginalTripleFstThd_le_marginalTripleThd (P : FinitePMF (α × β × γ)) (x : α) (z : γ) :
    marginalTripleFstThd P (x, z) ≤ marginalTripleThd P z := by
  have h_nonneg : ∀ x : α, 0 ≤ marginalTripleFstThd P (x, z) :=
    fun x => marginalTripleFstThd_nonneg P (x, z)
  have hle : marginalTripleFstThd P (x, z) ≤ ∑ x : α, marginalTripleFstThd P (x, z) :=
    Finset.single_le_sum (fun x _ => h_nonneg x) (Finset.mem_univ x)
  rwa [marginalTripleFstThd_sum_thd P z] at hle

lemma marginalTripleSndThd_le_marginalTripleThd (P : FinitePMF (α × β × γ)) (y : β) (z : γ) :
    marginalTripleSndThd P (y, z) ≤ marginalTripleThd P z := by
  have h_nonneg : ∀ y : β, 0 ≤ marginalTripleSndThd P (y, z) :=
    fun y => marginalTripleSndThd_nonneg P (y, z)
  have hle : marginalTripleSndThd P (y, z) ≤ ∑ y : β, marginalTripleSndThd P (y, z) :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ y)
  rwa [marginalTripleSndThd_sum_thd P z] at hle

/-! ## Aliases for backward compatibility -/

@[deprecated marginalPairFst (since := "2026-05-20")] alias marginalLeftMass := marginalPairFst
@[deprecated marginalPairSnd (since := "2026-05-20")] alias marginalRightMass := marginalPairSnd
@[deprecated marginalPairFst_nonneg (since := "2026-05-20")] alias marginalLeftMass_nonneg := marginalPairFst_nonneg
@[deprecated marginalPairSnd_nonneg (since := "2026-05-20")] alias marginalRightMass_nonneg := marginalPairSnd_nonneg
@[deprecated marginalPairFst_sum_one (since := "2026-05-20")] alias marginalLeftMass_sum_one := marginalPairFst_sum_one
@[deprecated marginalPairSnd_sum_one (since := "2026-05-20")] alias marginalRightMass_sum_one := marginalPairSnd_sum_one
@[deprecated marginalPairFst_le_one (since := "2026-05-20")] alias marginalLeftMass_le_one := marginalPairFst_le_one
@[deprecated marginalPairSnd_le_one (since := "2026-05-20")] alias marginalRightMass_le_one := marginalPairSnd_le_one
@[deprecated pmf_le_marginalPairFst (since := "2026-05-20")] alias pmf_le_marginalLeftMass := pmf_le_marginalPairFst
@[deprecated pmf_le_marginalPairSnd (since := "2026-05-20")] alias pmf_le_marginalRightMass := pmf_le_marginalPairSnd

end

end FiniteQuerySandbox
