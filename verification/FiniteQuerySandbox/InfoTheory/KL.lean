import FiniteQuerySandbox.InfoTheory.Basic

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

lemma kl_nonneg {α : Type} [Fintype α] [DecidableEq α]
    (p q : α → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x)
    (hq_pos : ∀ x, 0 < q x)
    (hp_sum : ∑ x, p x = 1)
    (hq_sum : ∑ x, q x = 1) :
    0 ≤ ∑ x, p x * Real.log (p x / q x) := by
  have h_term : ∀ x, p x * Real.log (p x / q x) ≥ p x - q x := by
    intro x
    by_cases hpx : p x = 0
    · -- p x = 0: LHS = 0 * log(0) = 0, need 0 ≥ -q x
      rw [hpx]
      have h0 : (0 : ℝ) / q x = 0 := by simp
      simp [h0]
      linarith [hq_pos x]
    · -- p x > 0
      have hpx_pos : 0 < p x := lt_of_le_of_ne (hp_nonneg x) (Ne.symm hpx)
      have h1 : Real.log (q x / p x) ≤ q x / p x - 1 :=
        Real.log_le_sub_one_of_pos (div_pos (hq_pos x) hpx_pos)
      have h2 : p x * Real.log (q x / p x) ≤ q x - p x := by
        have h_mul : p x * (q x / p x - 1) = q x - p x := by
          field_simp [hpx_pos.ne']
        have h3 : p x * Real.log (q x / p x) ≤ p x * (q x / p x - 1) := by
          apply mul_le_mul_of_nonneg_left h1 (le_of_lt hpx_pos)
        linarith [h3, h_mul]
      have h3 : p x * Real.log (p x / q x) = -(p x * Real.log (q x / p x)) := by
        rw [← mul_neg]
        congr
        rw [show Real.log (p x / q x) = -Real.log (q x / p x) by
          rw [Real.log_div (by exact hpx_pos.ne') (by exact (hq_pos x).ne')]
          rw [Real.log_div (by exact (hq_pos x).ne') (by exact hpx_pos.ne')]
          ring]
      rw [h3]
      linarith [h2]
  have hsum : ∑ x, p x * Real.log (p x / q x) ≥ ∑ x, (p x - q x) := by
    apply Finset.sum_le_sum
    intro x _
    exact h_term x
  have h_eq : ∑ x, (p x - q x) = 0 := by
    rw [Finset.sum_sub_distrib]
    linarith [hp_sum, hq_sum]
  linarith [hsum, h_eq]

lemma kl_nonneg_support {ι : Type} [Fintype ι] [DecidableEq ι]
    (p q : ι → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x)
    (hq_nonneg : ∀ x, 0 ≤ q x)
    (h_support : ∀ x, p x ≠ 0 → 0 < q x)
    (hp_sum : ∑ x, p x = 1)
    (hq_sum : ∑ x, q x = 1) :
    0 ≤ ∑ x, p x * Real.log (p x / q x) := by
  have h_term : ∀ x, p x * Real.log (p x / q x) ≥ p x - q x := by
    intro x
    by_cases hpx : p x = 0
    · rw [hpx]
      have h0 : (0 : ℝ) / q x = 0 := by simp
      simp [h0]
      linarith [hq_nonneg x]
    · have hpx_pos : 0 < p x := lt_of_le_of_ne (hp_nonneg x) (Ne.symm hpx)
      have hqx_pos : 0 < q x := h_support x hpx
      have h1 : Real.log (q x / p x) ≤ q x / p x - 1 :=
        Real.log_le_sub_one_of_pos (div_pos hqx_pos hpx_pos)
      have h2 : p x * Real.log (q x / p x) ≤ q x - p x := by
        have h_mul : p x * (q x / p x - 1) = q x - p x := by
          field_simp [hpx_pos.ne']
        have h3 : p x * Real.log (q x / p x) ≤ p x * (q x / p x - 1) := by
          apply mul_le_mul_of_nonneg_left h1 (le_of_lt hpx_pos)
        linarith [h3, h_mul]
      have h3 : p x * Real.log (p x / q x) = -(p x * Real.log (q x / p x)) := by
        rw [← mul_neg]
        congr
        rw [show Real.log (p x / q x) = -Real.log (q x / p x) by
          rw [Real.log_div (by exact hpx_pos.ne') (by exact hqx_pos.ne')]
          rw [Real.log_div (by exact hqx_pos.ne') (by exact hpx_pos.ne')]
          ring]
      rw [h3]
      linarith [h2]
  have hsum : ∑ x, p x * Real.log (p x / q x) ≥ ∑ x, (p x - q x) := by
    apply Finset.sum_le_sum
    intro x _
    exact h_term x
  have h_eq : ∑ x, (p x - q x) = 0 := by
    rw [Finset.sum_sub_distrib]
    linarith [hp_sum, hq_sum]
  linarith [hsum, h_eq]

end

end FiniteQuerySandbox
