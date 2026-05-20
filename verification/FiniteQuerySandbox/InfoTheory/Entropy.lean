import FiniteQuerySandbox.InfoTheory.KL

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

/-- Entropy of an arbitrary finite mass function, used for marginals. -/
def entropyOf {η : Type} [Fintype η] [DecidableEq η] (mass : η → ℝ) : ℝ :=
  ∑ x : η, negMulLog2 (mass x)

/-- Shannon entropy of a finite PMF, in bits. -/
def entropy (P : FinitePMF α) : ℝ :=
  entropyOf P.pmf

/-! ## Basic positivity lemmas -/

lemma negMulLog2_nonneg {p : ℝ} (hp_nonneg : 0 ≤ p) (hp_le_one : p ≤ 1) :
    0 ≤ negMulLog2 p := by
  unfold negMulLog2
  by_cases hp : p = 0
  · simp [hp]
  · have hp_pos : 0 < p := lt_of_le_of_ne hp_nonneg (Ne.symm hp)
    have hlog_le : Real.log p ≤ 0 :=
      (Real.log_le_sub_one_of_pos hp_pos).trans (by linarith : p - 1 ≤ 0)
    have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
    have h_div_le : Real.log p / Real.log 2 ≤ 0 :=
      div_nonpos_of_nonpos_of_nonneg hlog_le hlog2_pos.le
    have h_prod_le : p * (Real.log p / Real.log 2) ≤ 0 :=
      mul_nonpos_of_nonneg_of_nonpos hp_nonneg h_div_le
    linarith

lemma pmf_le_one (P : FinitePMF α) (x : α) :
    P.pmf x ≤ 1 := by
  have h_nonneg : ∀ y, 0 ≤ P.pmf y := P.pmf_nonneg
  have : P.pmf x ≤ ∑ y : α, P.pmf y :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ x)
  linarith [P.sum_one]

lemma entropy_nonneg (P : FinitePMF α) :
    0 ≤ entropy P := by
  unfold entropy entropyOf
  exact Finset.sum_nonneg (fun x _ => negMulLog2_nonneg (P.pmf_nonneg x) (pmf_le_one P x))

lemma entropyOf_equiv_eq {η θ : Type} [Fintype η] [DecidableEq η] [Fintype θ]
    [DecidableEq θ] (e : η ≃ θ) (f : η → ℝ) (g : θ → ℝ)
    (h : ∀ x, f x = g (e x)) :
    entropyOf f = entropyOf g := by
  unfold entropyOf
  calc
    ∑ x : η, negMulLog2 (f x)
        = ∑ x : η, negMulLog2 (g (e x)) := by
          refine Finset.sum_congr rfl (fun x _ => ?_)
          rw [h x]
    _ = ∑ y : θ, negMulLog2 (g y) := Equiv.sum_comp e (fun y => negMulLog2 (g y))

lemma entropyOf_mul_log2 {η : Type} [Fintype η] [DecidableEq η] (mass : η → ℝ) :
    entropyOf mass * Real.log 2 = -∑ x : η, mass x * Real.log (mass x) := by
  unfold entropyOf negMulLog2
  have hlog2_ne_zero : Real.log 2 ≠ 0 := by positivity
  rw [Finset.sum_mul]
  calc
    ∑ x : η, (-(mass x * (Real.log (mass x) / Real.log 2))) * Real.log 2
        = ∑ x : η, -(mass x * Real.log (mass x)) := by
          refine Finset.sum_congr rfl (fun x _ => ?_)
          field_simp [hlog2_ne_zero]
    _ = -∑ x : η, mass x * Real.log (mass x) := by
          rw [← Finset.sum_neg_distrib]

lemma Fintype.card_pos_of_finitePMF (P : FinitePMF α) :
    0 < Fintype.card α := by
  by_contra h
  push Not at h
  have hcard0 : Fintype.card α = 0 := by
    have h1 : Fintype.card α ≤ 0 := by linarith
    exact Nat.eq_zero_of_le_zero h1
  have hempty : IsEmpty α := Fintype.card_eq_zero_iff.mp hcard0
  have hempty2 : ∀ x : α, False := fun x => IsEmpty.false x
  have hsum0 : ∑ x : α, P.pmf x = 0 := by
    rw [Finset.sum_eq_zero]
    intro x _
    exact False.elim (hempty2 x)
  linarith [P.sum_one, hsum0]

lemma entropy_le_log_card (P : FinitePMF α) :
    entropy P ≤ Real.log (Fintype.card α) / Real.log 2 := by
  let q : α → ℝ := fun _ => 1 / Fintype.card α
  have hcard_pos : 0 < Fintype.card α := Fintype.card_pos_of_finitePMF P
  have hcard_real_pos : (0 : ℝ) < (Fintype.card α : ℝ) := by exact_mod_cast hcard_pos
  have hq_pos : ∀ x, 0 < q x := fun _ => by positivity
  have hq_sum : ∑ x, q x = 1 := by
    simp [q]
    field_simp [hcard_real_pos.ne']
  have h_kl := kl_nonneg P.pmf q P.pmf_nonneg hq_pos P.sum_one hq_sum
  have h_kl_expanded : ∑ x, P.pmf x * Real.log (P.pmf x / q x)
      = - (entropy P * Real.log 2) + Real.log (Fintype.card α) := by
    have h1 : ∀ x, P.pmf x * Real.log (P.pmf x / q x)
        = P.pmf x * Real.log (P.pmf x) + P.pmf x * Real.log (Fintype.card α) := by
      intro x
      have h_div : P.pmf x / q x = P.pmf x * (Fintype.card α : ℝ) := by
        simp [q]
      rw [h_div]
      by_cases hx : P.pmf x = 0
      · simp [hx]
      · rw [Real.log_mul (by exact hx) (by exact hcard_real_pos.ne')]
        ring
    have h2 : ∑ x, P.pmf x * Real.log (P.pmf x / q x)
        = ∑ x, (P.pmf x * Real.log (P.pmf x) + P.pmf x * Real.log (Fintype.card α)) := by
      apply Finset.sum_congr rfl
      intro x _
      exact h1 x
    rw [h2]
    rw [Finset.sum_add_distrib]
    have h3 : ∑ x : α, P.pmf x * Real.log (Fintype.card α) = Real.log (Fintype.card α) := by
      have h_const : ∑ x : α, P.pmf x * Real.log (Fintype.card α)
          = Real.log (Fintype.card α) * ∑ x : α, P.pmf x := by
        rw [Finset.mul_sum]
        simp [mul_comm]
      rw [h_const, P.sum_one]
      ring
    have h4 : ∑ x : α, P.pmf x * Real.log (P.pmf x) = - (entropy P * Real.log 2) := by
      have h5 : entropy P = ∑ x : α, -(P.pmf x * (Real.log (P.pmf x) / Real.log 2)) := by
        unfold entropy entropyOf negMulLog2
        rfl
      rw [h5]
      have hlog2_ne_zero : Real.log 2 ≠ 0 := by positivity
      have h6 : ∀ x, P.pmf x * Real.log (P.pmf x)
          = (-(P.pmf x * (Real.log (P.pmf x) / Real.log 2))) * (-Real.log 2) := by
        intro x
        field_simp [hlog2_ne_zero]
      simp_rw [h6]
      rw [← Finset.sum_mul]
      ring
    rw [h3, h4]
  rw [h_kl_expanded] at h_kl
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  have h_mul : entropy P * Real.log 2 ≤ Real.log (Fintype.card α) := by linarith [h_kl]
  have h_div : entropy P ≤ Real.log (Fintype.card α) / Real.log 2 := by
    apply (le_div_iff₀ (by positivity)).mpr
    linarith [h_mul]
  exact h_div

end

end FiniteQuerySandbox
