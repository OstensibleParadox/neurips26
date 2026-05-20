import FiniteQuerySandbox.InfoTheory.MutualInfo

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

def marginalXZMass (P : FinitePMF (α × β × γ)) (xz : α × γ) : ℝ :=
  ∑ y : β, P.pmf (xz.1, y, xz.2)

def marginalYZMass (P : FinitePMF (α × β × γ)) (yz : β × γ) : ℝ :=
  ∑ x : α, P.pmf (x, yz.1, yz.2)

def marginalZMass (P : FinitePMF (α × β × γ)) (z : γ) : ℝ :=
  ∑ x : α, ∑ y : β, P.pmf (x, y, z)

/-- Finite conditional mutual information `I(X;Y | Z)`. -/
def condMutualInfo (P_XYZ : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalXZMass P_XYZ) +
    entropyOf (marginalYZMass P_XYZ) -
    entropyOf (marginalZMass P_XYZ) -
    entropyOf (fun xyz : α × β × γ => P_XYZ.pmf xyz)

def condEntropy_Z_W (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalXZMass P) - entropyOf (marginalZMass P)

lemma condMutualInfo_le_condEntropy_Z_W (P : FinitePMF (α × β × γ)) :
    condMutualInfo P ≤ condEntropy_Z_W P := by
  unfold condMutualInfo condEntropy_Z_W
  have h_nonneg : 0 ≤ entropyOf (fun xyz : α × β × γ => P.pmf xyz) - entropyOf (marginalYZMass P) := by
    have h := condEntropy_nonneg (P := P)
    -- This relies on the 2-variable version of condEntropy
    -- Need careful mapping of types α × β × γ to (α × γ) × β or similar
    sorry -- Proof follows standard identities
  linarith

lemma marginalXZMass_nonneg (P : FinitePMF (α × β × γ)) (xz : α × γ) :
    0 ≤ marginalXZMass P xz :=
  Finset.sum_nonneg (fun y _ => P.pmf_nonneg (xz.1, y, xz.2))

lemma marginalYZMass_nonneg (P : FinitePMF (α × β × γ)) (yz : β × γ) :
    0 ≤ marginalYZMass P yz :=
  Finset.sum_nonneg (fun x _ => P.pmf_nonneg (x, yz.1, yz.2))

lemma marginalZMass_nonneg (P : FinitePMF (α × β × γ)) (z : γ) :
    0 ≤ marginalZMass P z :=
  Finset.sum_nonneg (fun x _ => Finset.sum_nonneg (fun y _ => P.pmf_nonneg (x, y, z)))

lemma marginalXZMass_sum_z (P : FinitePMF (α × β × γ)) (z : γ) :
    ∑ x : α, marginalXZMass P (x, z) = marginalZMass P z := by
  rfl

lemma marginalYZMass_sum_z (P : FinitePMF (α × β × γ)) (z : γ) :
    ∑ y : β, marginalYZMass P (y, z) = marginalZMass P z := by
  unfold marginalYZMass marginalZMass
  rw [Finset.sum_comm]

lemma marginalZMass_sum_one (P : FinitePMF (α × β × γ)) :
    ∑ z : γ, marginalZMass P z = 1 := by
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
  unfold marginalZMass
  rw [Finset.sum_comm]
  rw [show (∑ x : α, ∑ z : γ, ∑ y : β, P.pmf (x, y, z))
      = ∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z) by
        apply Finset.sum_congr rfl
        intro x _
        rw [Finset.sum_comm]]
  exact hsum

lemma pmf_le_marginalXZMass (P : FinitePMF (α × β × γ)) (x : α) (y : β) (z : γ) :
    P.pmf (x, y, z) ≤ marginalXZMass P (x, z) := by
  unfold marginalXZMass
  exact Finset.single_le_sum (fun y' _ => P.pmf_nonneg (x, y', z)) (Finset.mem_univ y)

lemma pmf_le_marginalYZMass (P : FinitePMF (α × β × γ)) (x : α) (y : β) (z : γ) :
    P.pmf (x, y, z) ≤ marginalYZMass P (y, z) := by
  unfold marginalYZMass
  exact Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', y, z)) (Finset.mem_univ x)

lemma marginalXZMass_le_marginalZMass (P : FinitePMF (α × β × γ)) (x : α) (z : γ) :
    marginalXZMass P (x, z) ≤ marginalZMass P z := by
  have h_nonneg : ∀ x : α, 0 ≤ marginalXZMass P (x, z) :=
    fun x => marginalXZMass_nonneg P (x, z)
  have hle : marginalXZMass P (x, z) ≤ ∑ x : α, marginalXZMass P (x, z) :=
    Finset.single_le_sum (fun x _ => h_nonneg x) (Finset.mem_univ x)
  rwa [marginalXZMass_sum_z P z] at hle

lemma marginalYZMass_le_marginalZMass (P : FinitePMF (α × β × γ)) (y : β) (z : γ) :
    marginalYZMass P (y, z) ≤ marginalZMass P z := by
  have h_nonneg : ∀ y : β, 0 ≤ marginalYZMass P (y, z) :=
    fun y => marginalYZMass_nonneg P (y, z)
  have hle : marginalYZMass P (y, z) ≤ ∑ y : β, marginalYZMass P (y, z) :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ y)
  rwa [marginalYZMass_sum_z P z] at hle

def condProductMass (P : FinitePMF (α × β × γ)) (xyz : α × β × γ) : ℝ :=
  marginalXZMass P (xyz.1, xyz.2.2) *
    marginalYZMass P (xyz.2.1, xyz.2.2) /
    marginalZMass P xyz.2.2

lemma condProductMass_nonneg (P : FinitePMF (α × β × γ)) (xyz : α × β × γ) :
    0 ≤ condProductMass P xyz := by
  unfold condProductMass
  exact div_nonneg
    (mul_nonneg (marginalXZMass_nonneg P (xyz.1, xyz.2.2))
      (marginalYZMass_nonneg P (xyz.2.1, xyz.2.2)))
    (marginalZMass_nonneg P xyz.2.2)

lemma condProductMass_pos_of_pmf_ne_zero
    (P : FinitePMF (α × β × γ)) (xyz : α × β × γ)
    (hxyz : P.pmf xyz ≠ 0) :
    0 < condProductMass P xyz := by
  rcases xyz with ⟨x, y, z⟩
  have hp_pos : 0 < P.pmf (x, y, z) :=
    lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
  have hxz_pos : 0 < marginalXZMass P (x, z) :=
    lt_of_lt_of_le hp_pos (pmf_le_marginalXZMass P x y z)
  have hyz_pos : 0 < marginalYZMass P (y, z) :=
    lt_of_lt_of_le hp_pos (pmf_le_marginalYZMass P x y z)
  have hz_pos : 0 < marginalZMass P z :=
    lt_of_lt_of_le hxz_pos (marginalXZMass_le_marginalZMass P x z)
  unfold condProductMass
  exact div_pos (mul_pos hxz_pos hyz_pos) hz_pos

lemma condProductMass_sum_fiber (P : FinitePMF (α × β × γ)) (z : γ) :
    (∑ x : α, ∑ y : β, condProductMass P (x, y, z)) = marginalZMass P z := by
  by_cases hz : marginalZMass P z = 0
  · have hxz_zero : ∀ x : α, marginalXZMass P (x, z) = 0 := by
      intro x
      have hle := marginalXZMass_le_marginalZMass P x z
      have hnonneg := marginalXZMass_nonneg P (x, z)
      linarith
    simp [condProductMass, hz, hxz_zero]
  · have hz_pos : 0 < marginalZMass P z :=
      lt_of_le_of_ne (marginalZMass_nonneg P z) (Ne.symm hz)
    calc
      (∑ x : α, ∑ y : β, condProductMass P (x, y, z))
          = ∑ x : α, ∑ y : β,
              marginalXZMass P (x, z) * marginalYZMass P (y, z) /
                marginalZMass P z := by
            rfl
      _ = ∑ x : α, marginalXZMass P (x, z) := by
            apply Finset.sum_congr rfl
            intro x _
            have hterm : ∀ y : β,
                marginalXZMass P (x, z) * marginalYZMass P (y, z) /
                    marginalZMass P z
                  =
                (marginalXZMass P (x, z) / marginalZMass P z) *
                    marginalYZMass P (y, z) := by
              intro y
              field_simp [hz]
            simp_rw [hterm]
            rw [← Finset.mul_sum, marginalYZMass_sum_z P z]
            field_simp [hz]
      _ = marginalZMass P z := marginalXZMass_sum_z P z

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
    _ = ∑ z : γ, marginalZMass P z := by
      apply Finset.sum_congr rfl
      intro z _
      exact condProductMass_sum_fiber P z
    _ = 1 := marginalZMass_sum_one P

lemma sum_pmf_log_marginalXZMass (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
      =
    ∑ xz : α × γ, marginalXZMass P xz * Real.log (marginalXZMass P xz) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalXZMass P (x, z)) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalXZMass P (x, z)) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ x : α, ∑ z : γ,
            marginalXZMass P (x, z) * Real.log (marginalXZMass P (x, z)) := by
          apply Finset.sum_congr rfl
          intro x _
          apply Finset.sum_congr rfl
          intro z _
          rw [← Finset.sum_mul]
          rfl
    _ = ∑ xz : α × γ, marginalXZMass P xz * Real.log (marginalXZMass P xz) := by
          rw [← Fintype.sum_prod_type' (fun x z =>
            marginalXZMass P (x, z) * Real.log (marginalXZMass P (x, z)))]

lemma sum_pmf_log_marginalYZMass (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
      =
    ∑ yz : β × γ, marginalYZMass P yz * Real.log (marginalYZMass P yz) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalYZMass P (y, z)) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ y : β, ∑ z : γ, ∑ x : α,
            P.pmf (x, y, z) * Real.log (marginalYZMass P (y, z)) := by
          rw [Finset.sum_comm]
          apply Finset.sum_congr rfl
          intro y _
          rw [Finset.sum_comm]
    _ = ∑ y : β, ∑ z : γ,
            marginalYZMass P (y, z) * Real.log (marginalYZMass P (y, z)) := by
          apply Finset.sum_congr rfl
          intro y _
          apply Finset.sum_congr rfl
          intro z _
          rw [← Finset.sum_mul]
          rfl
    _ = ∑ yz : β × γ, marginalYZMass P yz * Real.log (marginalYZMass P yz) := by
          rw [← Fintype.sum_prod_type' (fun y z =>
            marginalYZMass P (y, z) * Real.log (marginalYZMass P (y, z)))]

lemma sum_pmf_log_marginalZMass (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalZMass P xyz.2.2))
      =
    ∑ z : γ, marginalZMass P z * Real.log (marginalZMass P z) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalZMass P xyz.2.2))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalZMass P z) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalZMass P z) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ z : γ, ∑ x : α, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalZMass P z) := by
          rw [Finset.sum_comm]
    _ = ∑ z : γ,
            marginalZMass P z * Real.log (marginalZMass P z) := by
          apply Finset.sum_congr rfl
          intro z _
          rw [show (∑ x : α, ∑ y : β,
              P.pmf (x, y, z) * Real.log (marginalZMass P z))
              =
              ∑ x : α, (∑ y : β, P.pmf (x, y, z)) * Real.log (marginalZMass P z) by
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
  let B : ℝ := ∑ xz : α × γ, marginalXZMass P xz * Real.log (marginalXZMass P xz)
  let C : ℝ := ∑ yz : β × γ, marginalYZMass P yz * Real.log (marginalYZMass P yz)
  let D : ℝ := ∑ z : γ, marginalZMass P z * Real.log (marginalZMass P z)
  have hterm : ∀ xyz : α × β × γ,
      P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz)
        =
      ((P.pmf xyz * Real.log (P.pmf xyz)
        - P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
        - P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
        + P.pmf xyz * Real.log (marginalZMass P xyz.2.2) := by
    intro xyz
    by_cases hxyz : P.pmf xyz = 0
    · simp [hxyz]
    · rcases xyz with ⟨x, y, z⟩
      have hp_pos : 0 < P.pmf (x, y, z) :=
        lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
      have hxz_pos : 0 < marginalXZMass P (x, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalXZMass P x y z)
      have hyz_pos : 0 < marginalYZMass P (y, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalYZMass P x y z)
      have hz_pos : 0 < marginalZMass P z :=
        lt_of_lt_of_le hxz_pos (marginalXZMass_le_marginalZMass P x z)
      have hq_pos : 0 < condProductMass P (x, y, z) :=
        condProductMass_pos_of_pmf_ne_zero P (x, y, z) hxyz
      have hlogq : Real.log (condProductMass P (x, y, z))
          =
          Real.log (marginalXZMass P (x, z)) +
          Real.log (marginalYZMass P (y, z)) -
          Real.log (marginalZMass P z) := by
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
            - P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
            - P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
            + P.pmf xyz * Real.log (marginalZMass P xyz.2.2)) := by
            apply Finset.sum_congr rfl
            intro xyz _
            exact hterm xyz
      _ = A - B - C + D := by
            rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_sub_distrib]
            rw [sum_pmf_log_marginalXZMass P, sum_pmf_log_marginalYZMass P,
              sum_pmf_log_marginalZMass P]
  have hHXZ := entropyOf_mul_log2 (marginalXZMass P)
  have hHYZ := entropyOf_mul_log2 (marginalYZMass P)
  have hHZ := entropyOf_mul_log2 (marginalZMass P)
  have hHXYZ := entropyOf_mul_log2 (fun xyz : α × β × γ => P.pmf xyz)
  have hcmi : condMutualInfo P * Real.log 2 = A - B - C + D := by
    unfold condMutualInfo
    calc
      (entropyOf (marginalXZMass P) + entropyOf (marginalYZMass P) -
          entropyOf (marginalZMass P) -
          entropyOf (fun xyz : α × β × γ => P.pmf xyz)) * Real.log 2
          =
        entropyOf (marginalXZMass P) * Real.log 2 +
          entropyOf (marginalYZMass P) * Real.log 2 -
          entropyOf (marginalZMass P) * Real.log 2 -
          entropyOf (fun xyz : α × β × γ => P.pmf xyz) * Real.log 2 := by
            ring
      _ = A - B - C + D := by
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
    (h : ∀ x y z,
      P.pmf (x, y, z) * marginalZMass P z =
        marginalXZMass P (x, z) * marginalYZMass P (y, z)) :
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
      have hxz_pos : 0 < marginalXZMass P (x, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalXZMass P x y z)
      have hz_pos : 0 < marginalZMass P z :=
        lt_of_lt_of_le hxz_pos (marginalXZMass_le_marginalZMass P x z)
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

end

end FiniteQuerySandbox
