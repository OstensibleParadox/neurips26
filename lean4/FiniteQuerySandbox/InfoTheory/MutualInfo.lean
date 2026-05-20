import FiniteQuerySandbox.InfoTheory.Entropy
import FiniteQuerySandbox.InfoTheory.Marginal
import FiniteQuerySandbox.InfoTheory.KL

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

/-- Finite conditional entropy `H(X | Y) = H(X,Y) - H(Y)`. -/
def condEntropy (P_XY : FinitePMF (α × β)) : ℝ :=
  entropyOf (fun xy : α × β => P_XY.pmf xy) -
    entropyOf (marginalPairSnd P_XY)

/-- Mutual information I(X;Y) for a 2-variable PMF. -/
def mutualInfo (P : FinitePMF (α × β)) : ℝ :=
  entropyOf (marginalPairFst P) + entropyOf (marginalPairSnd P) - entropyOf P.pmf

/-- Product of marginals P_X * P_Y as a reference distribution. -/
def productMarginalMass (P : FinitePMF (α × β)) (xy : α × β) : ℝ :=
  marginalPairFst P xy.1 * marginalPairSnd P xy.2

lemma productMarginalMass_nonneg (P : FinitePMF (α × β)) (xy : α × β) :
    0 ≤ productMarginalMass P xy :=
  mul_nonneg (marginalPairFst_nonneg P xy.1) (marginalPairSnd_nonneg P xy.2)

lemma productMarginalMass_pos_of_pmf_ne_zero
    (P : FinitePMF (α × β)) (xy : α × β)
    (hxy : P.pmf xy ≠ 0) :
    0 < productMarginalMass P xy := by
  have h_left : 0 < marginalPairFst P xy.1 :=
    lt_of_lt_of_le (lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy))
      (Finset.single_le_sum (fun y' _ => P.pmf_nonneg (xy.1, y')) (Finset.mem_univ xy.2))
  have h_right : 0 < marginalPairSnd P xy.2 :=
    lt_of_lt_of_le (lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy))
      (Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', xy.2)) (Finset.mem_univ xy.1))
  exact mul_pos h_left h_right

lemma productMarginalMass_sum_one (P : FinitePMF (α × β)) :
    ∑ xy : α × β, productMarginalMass P xy = 1 := by
  unfold productMarginalMass
  calc
    ∑ xy : α × β, marginalPairFst P xy.1 * marginalPairSnd P xy.2
        = ∑ x : α, ∑ y : β, marginalPairFst P x * marginalPairSnd P y := by
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, (marginalPairFst P x * ∑ y : β, marginalPairSnd P y) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.mul_sum]
    _ = ∑ x : α, marginalPairFst P x * 1 := by
          rw [marginalPairSnd_sum_one]
    _ = 1 := by
          simp
          exact marginalPairFst_sum_one P

lemma sum_pmf_log_marginalLeftMass (P : FinitePMF (α × β)) :
    (∑ xy : α × β, P.pmf xy * Real.log (marginalPairFst P xy.1))
      =
    ∑ x : α, marginalPairFst P x * Real.log (marginalPairFst P x) := by
  calc
    (∑ xy : α × β, P.pmf xy * Real.log (marginalPairFst P xy.1))
        = ∑ x : α, ∑ y : β, P.pmf (x, y) * Real.log (marginalPairFst P x) := by
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, (∑ y : β, P.pmf (x, y)) * Real.log (marginalPairFst P x) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [← Finset.sum_mul]
    _ = ∑ x : α, marginalPairFst P x * Real.log (marginalPairFst P x) := rfl

lemma sum_pmf_log_marginalRightMass (P : FinitePMF (α × β)) :
    (∑ xy : α × β, P.pmf xy * Real.log (marginalPairSnd P xy.2))
      =
    ∑ y : β, marginalPairSnd P y * Real.log (marginalPairSnd P y) := by
  calc
    (∑ xy : α × β, P.pmf xy * Real.log (marginalPairSnd P xy.2))
        = ∑ x : α, ∑ y : β, P.pmf (x, y) * Real.log (marginalPairSnd P y) := by
          rw [Fintype.sum_prod_type]
    _ = ∑ y : β, ∑ x : α, P.pmf (x, y) * Real.log (marginalPairSnd P y) := by
          rw [Finset.sum_comm]
    _ = ∑ y : β, (∑ x : α, P.pmf (x, y)) * Real.log (marginalPairSnd P y) := by
          apply Finset.sum_congr rfl
          intro y _
          rw [← Finset.sum_mul]
    _ = ∑ y : β, marginalPairSnd P y * Real.log (marginalPairSnd P y) := rfl

lemma condEntropy_mul_log2 (P : FinitePMF (α × β)) :
    condEntropy P * Real.log 2 =
      ∑ xy : α × β, P.pmf xy * Real.log (marginalPairSnd P xy.2 / P.pmf xy) := by
    have hJoint := entropyOf_mul_log2 (fun xy : α × β => P.pmf xy)
    have hMarg := entropyOf_mul_log2 (marginalPairSnd P)
    unfold condEntropy
    calc
      (entropyOf (fun xy : α × β => P.pmf xy) - entropyOf (marginalPairSnd P)) * Real.log 2
          = entropyOf (fun xy : α × β => P.pmf xy) * Real.log 2 -
              entropyOf (marginalPairSnd P) * Real.log 2 := by ring
      _ = (-∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy)) -
            (-∑ y : β, marginalPairSnd P y * Real.log (marginalPairSnd P y)) := by
            rw [hJoint, hMarg]
      _ = -∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy) +
            ∑ xy : α × β, P.pmf xy * Real.log (marginalPairSnd P xy.2) := by
            rw [sum_pmf_log_marginalRightMass P]
            ring
      _ = ∑ xy : α × β,
            (P.pmf xy * Real.log (marginalPairSnd P xy.2) -
              P.pmf xy * Real.log (P.pmf xy)) := by
            rw [Finset.sum_sub_distrib]
            ring
      _ = ∑ xy : α × β,
            P.pmf xy * Real.log (marginalPairSnd P xy.2 / P.pmf xy) := by
            apply Finset.sum_congr rfl
            intro xy _
            by_cases hxy : P.pmf xy = 0
            · simp [hxy]
            · have hp_pos : 0 < P.pmf xy :=
                lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy)
              have hm_pos : 0 < marginalPairSnd P xy.2 :=
                lt_of_lt_of_le hp_pos (pmf_le_marginalPairSnd P xy.1 xy.2)
              rw [Real.log_div hm_pos.ne' hp_pos.ne']
              ring

lemma condEntropy_nonneg (P : FinitePMF (α × β)) :
    0 ≤ condEntropy P := by
  have hmul_eq := condEntropy_mul_log2 (P := P)
  have hsum_nonneg :
      0 ≤ ∑ xy : α × β,
        P.pmf xy * Real.log (marginalPairSnd P xy.2 / P.pmf xy) := by
    apply Finset.sum_nonneg
    intro xy _
    by_cases hxy : P.pmf xy = 0
    · simp [hxy]
    · have hp_pos : 0 < P.pmf xy :=
        lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy)
      have hle : P.pmf xy ≤ marginalPairSnd P xy.2 :=
        pmf_le_marginalPairSnd P xy.1 xy.2
      have hratio_ge_one : 1 ≤ marginalPairSnd P xy.2 / P.pmf xy := by
        rw [le_div_iff₀ hp_pos]
        simpa using hle
      exact mul_nonneg hp_pos.le (Real.log_nonneg hratio_ge_one)
  have hmul_nonneg : 0 ≤ condEntropy P * Real.log 2 := by
    rw [hmul_eq]
    exact hsum_nonneg
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  by_contra hneg
  push Not at hneg
  have hmul_neg : condEntropy P * Real.log 2 < 0 :=
    mul_neg_of_neg_of_pos hneg hlog2_pos
  linarith

lemma mutualInfo_kl_identity (P : FinitePMF (α × β)) :
    (∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy))
    = mutualInfo P * Real.log 2 := by
  let A : ℝ := ∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy)
  let B : ℝ := ∑ x : α, marginalPairFst P x * Real.log (marginalPairFst P x)
  let C : ℝ := ∑ y : β, marginalPairSnd P y * Real.log (marginalPairSnd P y)
  have hterm : ∀ xy : α × β,
      P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy)
        =
      P.pmf xy * Real.log (P.pmf xy) - P.pmf xy * Real.log (marginalPairFst P xy.1)
        - P.pmf xy * Real.log (marginalPairSnd P xy.2) := by
    intro xy
    by_cases hxy : P.pmf xy = 0
    · simp [hxy]
    · have hp_pos : 0 < P.pmf xy := lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy)
      have h_left_pos : 0 < marginalPairFst P xy.1 :=
        lt_of_lt_of_le hp_pos (Finset.single_le_sum (fun y' _ => P.pmf_nonneg (xy.1, y')) (Finset.mem_univ xy.2))
      have h_right_pos : 0 < marginalPairSnd P xy.2 :=
        lt_of_lt_of_le hp_pos (Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', xy.2)) (Finset.mem_univ xy.1))
      have hq_pos : 0 < productMarginalMass P xy := mul_pos h_left_pos h_right_pos
      rw [Real.log_div hp_pos.ne' hq_pos.ne']
      unfold productMarginalMass
      rw [Real.log_mul h_left_pos.ne' h_right_pos.ne']
      ring
  have hsum :
      (∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy))
        = A - B - C := by
    calc
      (∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy))
          = ∑ xy : α × β, (P.pmf xy * Real.log (P.pmf xy) - P.pmf xy * Real.log (marginalPairFst P xy.1)
              - P.pmf xy * Real.log (marginalPairSnd P xy.2)) := by
            apply Finset.sum_congr rfl
            intro xy _
            exact hterm xy
      _ = A - B - C := by
            rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib]
            rw [sum_pmf_log_marginalLeftMass P, sum_pmf_log_marginalRightMass P]
  have hHL := entropyOf_mul_log2 (marginalPairFst P)
  have hHR := entropyOf_mul_log2 (marginalPairSnd P)
  have hHFull := entropyOf_mul_log2 P.pmf
  have hmi : mutualInfo P * Real.log 2 = A - B - C := by
    unfold mutualInfo
    calc
      (entropyOf (marginalPairFst P) + entropyOf (marginalPairSnd P) - entropyOf P.pmf) * Real.log 2
          = entropyOf (marginalPairFst P) * Real.log 2 + entropyOf (marginalPairSnd P) * Real.log 2
              - entropyOf P.pmf * Real.log 2 := by ring
      _ = A - B - C := by
            rw [hHL, hHR, hHFull]
            simp [A, B, C]
            ring
  rw [hsum, hmi]

lemma mutualInfo_nonneg (P : FinitePMF (α × β)) :
    0 ≤ mutualInfo P := by
  have hkl := kl_nonneg_support P.pmf (productMarginalMass P)
    P.pmf_nonneg
    (productMarginalMass_nonneg P)
    (productMarginalMass_pos_of_pmf_ne_zero P)
    P.sum_one
    (productMarginalMass_sum_one P)
  rw [mutualInfo_kl_identity P] at hkl
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  by_contra hneg
  push Not at hneg
  have hmul_neg : mutualInfo P * Real.log 2 < 0 :=
    mul_neg_of_neg_of_pos hneg hlog2_pos
  linarith

end

end FiniteQuerySandbox
