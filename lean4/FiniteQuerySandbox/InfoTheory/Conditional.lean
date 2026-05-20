import FiniteQuerySandbox.InfoTheory.MutualInfo

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

/-- Finite conditional mutual information `I(X;Y | Z)`. -/
def condMutualInfo (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalTripleFstThd P) +
    entropyOf (marginalTripleSndThd P) -
    entropyOf (marginalTripleThd P) -
    entropy P

/-- Conditional Independence -/
def condIndep (P : FinitePMF (α × β × γ)) : Prop :=
  ∀ a b z,
    P.pmf (a, b, z) * marginalTripleThd P z =
      marginalTripleFstThd P (a, z) * marginalTripleSndThd P (b, z)

def condProductMass (P : FinitePMF (α × β × γ)) (xyz : α × β × γ) : ℝ :=
  marginalTripleFstThd P (xyz.1, xyz.2.2) *
    marginalTripleSndThd P (xyz.2.1, xyz.2.2) /
    marginalTripleThd P xyz.2.2

lemma condProductMass_nonneg (P : FinitePMF (α × β × γ)) (xyz : α × β × γ) :
    0 ≤ condProductMass P xyz := by
  unfold condProductMass
  exact div_nonneg
    (mul_nonneg (marginalTripleFstThd_nonneg P (xyz.1, xyz.2.2))
      (marginalTripleSndThd_nonneg P (xyz.2.1, xyz.2.2)))
    (marginalTripleThd_nonneg P xyz.2.2)

lemma condProductMass_pos_of_pmf_ne_zero
    (P : FinitePMF (α × β × γ)) (xyz : α × β × γ)
    (hxyz : P.pmf xyz ≠ 0) :
    0 < condProductMass P xyz := by
  rcases xyz with ⟨x, y, z⟩
  have hp_pos : 0 < P.pmf (x, y, z) :=
    lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
  have hxz_pos : 0 < marginalTripleFstThd P (x, z) :=
    lt_of_lt_of_le hp_pos (pmf_le_marginalTripleFstThd P x y z)
  have hyz_pos : 0 < marginalTripleSndThd P (y, z) :=
    lt_of_lt_of_le hp_pos (pmf_le_marginalTripleSndThd P x y z)
  have hz_pos : 0 < marginalTripleThd P z :=
    lt_of_lt_of_le hxz_pos (marginalTripleFstThd_le_marginalTripleThd P x z)
  unfold condProductMass
  exact div_pos (mul_pos hxz_pos hyz_pos) hz_pos

lemma condProductMass_sum_fiber (P : FinitePMF (α × β × γ)) (z : γ) :
    (∑ x : α, ∑ y : β, condProductMass P (x, y, z)) = marginalTripleThd P z := by
  by_cases hz : marginalTripleThd P z = 0
  · have hxz_zero : ∀ x : α, marginalTripleFstThd P (x, z) = 0 := by
      intro x
      have hle := marginalTripleFstThd_le_marginalTripleThd P x z
      have hnonneg := marginalTripleFstThd_nonneg P (x, z)
      linarith
    simp [condProductMass, hz, hxz_zero]
  · have hz_pos : 0 < marginalTripleThd P z :=
      lt_of_le_of_ne (marginalTripleThd_nonneg P z) (Ne.symm hz)
    calc
      (∑ x : α, ∑ y : β, condProductMass P (x, y, z))
          = ∑ x : α, ∑ y : β,
              (marginalTripleFstThd P (x, z) * marginalTripleSndThd P (y, z)) /
                marginalTripleThd P z := rfl
      _ = ∑ x : α, ∑ y : β, (marginalTripleFstThd P (x, z) / marginalTripleThd P z) *
              marginalTripleSndThd P (y, z) := by
            apply Finset.sum_congr rfl
            intro x _
            apply Finset.sum_congr rfl
            intro y _
            field_simp [hz]
      _ = ∑ x : α, (marginalTripleFstThd P (x, z) / marginalTripleThd P z) *
              ∑ y : β, marginalTripleSndThd P (y, z) := by
            apply Finset.sum_congr rfl
            intro x _
            rw [Finset.mul_sum]
      _ = ∑ x : α, marginalTripleFstThd P (x, z) := by
            simp_rw [marginalTripleSndThd_sum_thd P z]
            apply Finset.sum_congr rfl
            intro x _
            field_simp [hz]
      _ = marginalTripleThd P z := marginalTripleFstThd_sum_thd P z

lemma condProductMass_sum_one (P : FinitePMF (α × β × γ)) :
    ∑ xyz : α × β × γ, condProductMass P xyz = 1 := by
  calc
    ∑ xyz : α × β × γ, condProductMass P xyz
        = ∑ x : α, ∑ y : β, ∑ z : γ, condProductMass P (x, y, z) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β, condProductMass P (x, y, z) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ z : γ, ∑ x : α, ∑ y : β, condProductMass P (x, y, z) := by
          rw [Finset.sum_comm]
    _ = ∑ z : γ, marginalTripleThd P z := by
      apply Finset.sum_congr rfl
      intro z _
      exact condProductMass_sum_fiber P z
    _ = 1 := marginalTripleThd_sum_one P

lemma sum_pmf_log_marginalTripleFstThd (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalTripleFstThd P (xyz.1, xyz.2.2)))
      =
    ∑ xz : α × γ, marginalTripleFstThd P xz * Real.log (marginalTripleFstThd P xz) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalTripleFstThd P (xyz.1, xyz.2.2)))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalTripleFstThd P (x, z)) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalTripleFstThd P (x, z)) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ x : α, ∑ z : γ,
            marginalTripleFstThd P (x, z) * Real.log (marginalTripleFstThd P (x, z)) := by
          apply Finset.sum_congr rfl
          intro x _
          apply Finset.sum_congr rfl
          intro z _
          rw [← Finset.sum_mul]
          rfl
    _ = ∑ xz : α × γ, marginalTripleFstThd P xz * Real.log (marginalTripleFstThd P xz) := by
          rw [← Fintype.sum_prod_type' (fun x z =>
            marginalTripleFstThd P (x, z) * Real.log (marginalTripleFstThd P (x, z)))]

lemma sum_pmf_log_marginalTripleSndThd (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalTripleSndThd P (xyz.2.1, xyz.2.2)))
      =
    ∑ yz : β × γ, marginalTripleSndThd P yz * Real.log (marginalTripleSndThd P yz) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalTripleSndThd P (xyz.2.1, xyz.2.2)))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalTripleSndThd P (y, z)) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ y : β, ∑ z : γ, ∑ x : α,
            P.pmf (x, y, z) * Real.log (marginalTripleSndThd P (y, z)) := by
          rw [Finset.sum_comm]
          apply Finset.sum_congr rfl
          intro y _
          rw [Finset.sum_comm]
    _ = ∑ y : β, ∑ z : γ,
            marginalTripleSndThd P (y, z) * Real.log (marginalTripleSndThd P (y, z)) := by
          apply Finset.sum_congr rfl
          intro y _
          apply Finset.sum_congr rfl
          intro z _
          rw [← Finset.sum_mul]
          rfl
    _ = ∑ yz : β × γ, marginalTripleSndThd P yz * Real.log (marginalTripleSndThd P yz) := by
          rw [← Fintype.sum_prod_type' (fun y z =>
            marginalTripleSndThd P (y, z) * Real.log (marginalTripleSndThd P (y, z)))]

lemma sum_pmf_log_marginalTripleThd (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalTripleThd P xyz.2.2))
      =
    ∑ z : γ, marginalTripleThd P z * Real.log (marginalTripleThd P z) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalTripleThd P xyz.2.2))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalTripleThd P z) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalTripleThd P z) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ z : γ, ∑ x : α, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalTripleThd P z) := by
          rw [Finset.sum_comm]
    _ = ∑ z : γ,
            marginalTripleThd P z * Real.log (marginalTripleThd P z) := by
          apply Finset.sum_congr rfl
          intro z _
          rw [show (∑ x : α, ∑ y : β,
              P.pmf (x, y, z) * Real.log (marginalTripleThd P z))
              =
              ∑ x : α, (∑ y : β, P.pmf (x, y, z)) * Real.log (marginalTripleThd P z) by
                apply Finset.sum_congr rfl
                intro x _
                rw [← Finset.sum_mul]]
          rw [← Finset.sum_mul]
          rfl

lemma condMutualInfo_kl_identity (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz))
      =
    condMutualInfo P * Real.log 2 := by
  let A : ℝ := ∑ xyz : α × β × γ, P.pmf xyz * Real.log (P.pmf xyz)
  let B : ℝ := ∑ xz : α × γ, marginalTripleFstThd P xz * Real.log (marginalTripleFstThd P xz)
  let C : ℝ := ∑ yz : β × γ, marginalTripleSndThd P yz * Real.log (marginalTripleSndThd P yz)
  let D : ℝ := ∑ z : γ, marginalTripleThd P z * Real.log (marginalTripleThd P z)
  have hterm : ∀ xyz : α × β × γ,
      P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz)
        =
      ((P.pmf xyz * Real.log (P.pmf xyz)
        - P.pmf xyz * Real.log (marginalTripleFstThd P (xyz.1, xyz.2.2)))
        - P.pmf xyz * Real.log (marginalTripleSndThd P (xyz.2.1, xyz.2.2)))
        + P.pmf xyz * Real.log (marginalTripleThd P xyz.2.2) := by
    intro xyz
    by_cases hxyz : P.pmf xyz = 0
    · simp [hxyz]
    · rcases xyz with ⟨x, y, z⟩
      have hp_pos : 0 < P.pmf (x, y, z) :=
        lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
      have hxz_pos : 0 < marginalTripleFstThd P (x, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalTripleFstThd P x y z)
      have hyz_pos : 0 < marginalTripleSndThd P (y, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalTripleSndThd P x y z)
      have hz_pos : 0 < marginalTripleThd P z :=
        lt_of_lt_of_le hxz_pos (marginalTripleFstThd_le_marginalTripleThd P x z)
      have hq_pos : 0 < condProductMass P (x, y, z) :=
        condProductMass_pos_of_pmf_ne_zero P (x, y, z) hxyz
      have hlogq : Real.log (condProductMass P (x, y, z))
          =
          Real.log (marginalTripleFstThd P (x, z)) +
          Real.log (marginalTripleSndThd P (y, z)) -
          Real.log (marginalTripleThd P z) := by
        unfold condProductMass
        rw [Real.log_div (mul_ne_zero hxz_pos.ne' hyz_pos.ne') hz_pos.ne']
        rw [Real.log_mul hxz_pos.ne' hyz_pos.ne']
      rw [Real.log_div hp_pos.ne' hq_pos.ne', hlogq]
      ring
  have hsum :
      (∑ xyz : α × β × γ,
        P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz))
        = A - B - C + D := by
    calc
      (∑ xyz : α × β × γ,
        P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz))
          =
        ∑ xyz : α × β × γ,
          (((P.pmf xyz * Real.log (P.pmf xyz)
            - P.pmf xyz * Real.log (marginalTripleFstThd P (xyz.1, xyz.2.2)))
            - P.pmf xyz * Real.log (marginalTripleSndThd P (xyz.2.1, xyz.2.2)))
            + P.pmf xyz * Real.log (marginalTripleThd P xyz.2.2)) := by
            apply Finset.sum_congr rfl
            intro xyz _
            exact hterm xyz
      _ = A - B - C + D := by
            rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_sub_distrib]
            rw [sum_pmf_log_marginalTripleFstThd P, sum_pmf_log_marginalTripleSndThd P,
              sum_pmf_log_marginalTripleThd P]
  have hHXZ := entropyOf_mul_log2 (marginalTripleFstThd P)
  have hHYZ := entropyOf_mul_log2 (marginalTripleSndThd P)
  have hHZ := entropyOf_mul_log2 (marginalTripleThd P)
  have hHXYZ := entropyOf_mul_log2 (fun xyz : α × β × γ => P.pmf xyz)
  have hcmi : condMutualInfo P * Real.log 2 = A - B - C + D := by
    unfold condMutualInfo
    calc
      (entropyOf (marginalTripleFstThd P) + entropyOf (marginalTripleSndThd P) -
          entropyOf (marginalTripleThd P) -
          entropy P) * Real.log 2
          =
        entropyOf (marginalTripleFstThd P) * Real.log 2 +
          entropyOf (marginalTripleSndThd P) * Real.log 2 -
          entropyOf (marginalTripleThd P) * Real.log 2 -
          entropy P * Real.log 2 := by
            ring
      _ = A - B - C + D := by
            unfold entropy
            rw [hHXZ, hHYZ, hHZ, hHXYZ]
            simp [A, B, C, D]
            ring
  rw [hsum, hcmi]

lemma condMutualInfo_nonneg (P : FinitePMF (α × β × γ)) :
    0 ≤ condMutualInfo P := by
  have hkl := kl_nonneg_support P.pmf (condProductMass P)
    P.pmf_nonneg
    (condProductMass_nonneg P)
    (condProductMass_pos_of_pmf_ne_zero P)
    P.sum_one
    (condProductMass_sum_one P)
  rw [condMutualInfo_kl_identity P] at hkl
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  by_contra hneg
  push Not at hneg
  have hmul_neg : condMutualInfo P * Real.log 2 < 0 :=
    mul_neg_of_neg_of_pos hneg hlog2_pos
  linarith

lemma condMutualInfo_eq_zero_of_condIndep
    (P : FinitePMF (α × β × γ))
    (h : condIndep P) :
    condMutualInfo P = 0 := by
  have hkl_zero :
      (∑ xyz : α × β × γ,
        P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz)) = 0 := by
    apply Finset.sum_eq_zero
    intro xyz _
    by_cases hxyz : P.pmf xyz = 0
    · simp [hxyz]
    · rcases xyz with ⟨x, y, z⟩
      have hp_pos : 0 < P.pmf (x, y, z) :=
        lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
      have hxz_pos : 0 < marginalTripleFstThd P (x, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalTripleFstThd P x y z)
      have hz_pos : 0 < marginalTripleThd P z :=
        lt_of_lt_of_le hxz_pos (marginalTripleFstThd_le_marginalTripleThd P x z)
      have hq_eq : condProductMass P (x, y, z) = P.pmf (x, y, z) := by
        unfold condProductMass
        rw [← h x y z]
        field_simp [hz_pos.ne']
      rw [hq_eq]
      simp [hxyz]
  have hmul : condMutualInfo P * Real.log 2 = 0 := by
    rw [← condMutualInfo_kl_identity P, hkl_zero]
  have hlog2_ne : Real.log 2 ≠ 0 := by positivity
  exact (mul_eq_zero.mp hmul).resolve_right hlog2_ne

/-! ## Aliases for backward compatibility -/

@[deprecated marginalTripleFstThd (since := "2026-05-20")] alias marginalXZMass := marginalTripleFstThd
@[deprecated marginalTripleSndThd (since := "2026-05-20")] alias marginalYZMass := marginalTripleSndThd
@[deprecated marginalTripleThd (since := "2026-05-20")] alias marginalZMass := marginalTripleThd
@[deprecated marginalTripleFstThd_nonneg (since := "2026-05-20")] alias marginalXZMass_nonneg := marginalTripleFstThd_nonneg
@[deprecated marginalTripleSndThd_nonneg (since := "2026-05-20")] alias marginalYZMass_nonneg := marginalTripleSndThd_nonneg
@[deprecated marginalTripleThd_nonneg (since := "2026-05-20")] alias marginalZMass_nonneg := marginalTripleThd_nonneg
@[deprecated marginalTripleFstThd_sum_thd (since := "2026-05-20")] alias marginalXZMass_sum_z := marginalTripleFstThd_sum_thd
@[deprecated marginalTripleSndThd_sum_thd (since := "2026-05-20")] alias marginalYZMass_sum_z := marginalTripleSndThd_sum_thd
@[deprecated marginalTripleThd_sum_one (since := "2026-05-20")] alias marginalZMass_sum_one := marginalTripleThd_sum_one
@[deprecated pmf_le_marginalTripleFstThd (since := "2026-05-20")] alias pmf_le_marginalXZMass := pmf_le_marginalTripleFstThd
@[deprecated pmf_le_marginalTripleSndThd (since := "2026-05-20")] alias pmf_le_marginalYZMass := pmf_le_marginalTripleSndThd
@[deprecated marginalTripleFstThd_le_marginalTripleThd (since := "2026-05-20")] alias marginalXZMass_le_marginalZMass := marginalTripleFstThd_le_marginalTripleThd
@[deprecated marginalTripleSndThd_le_marginalTripleThd (since := "2026-05-20")] alias marginalYZMass_le_marginalZMass := marginalTripleSndThd_le_marginalTripleThd

end

end FiniteQuerySandbox
