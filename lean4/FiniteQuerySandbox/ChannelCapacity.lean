import Mathlib
import FiniteQuerySandbox.InfoTheory

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

/-! ## Marginal of Y from a 4-variable PMF -/

/-- Marginal distribution of Y from a 4-variable PMF P(x, y, z, w). -/
def marginalYMass {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P : FinitePMF (α × β × γ × δ)) (y : β) : ℝ :=
  ∑ x : α, ∑ z : γ, ∑ w : δ, P.pmf (x, y, z, w)

lemma marginalYMass_nonneg {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P : FinitePMF (α × β × γ × δ)) (y : β) : 0 ≤ marginalYMass P y := by
  unfold marginalYMass
  apply Finset.sum_nonneg
  intro x _
  apply Finset.sum_nonneg
  intro z _
  apply Finset.sum_nonneg
  intro w _
  exact P.pmf_nonneg (x, y, z, w)

lemma marginalYMass_sum_one {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P : FinitePMF (α × β × γ × δ)) : ∑ y : β, marginalYMass P y = 1 := by
  unfold marginalYMass
  calc
    ∑ y : β, ∑ x : α, ∑ z : γ, ∑ w : δ, P.pmf (x, y, z, w) =
      ∑ x : α, ∑ y : β, ∑ z : γ, ∑ w : δ, P.pmf (x, y, z, w) := by
      rw [Finset.sum_comm]
    _ = 1 := by
      simpa [Fintype.sum_prod_type] using P.sum_one

lemma marginalYMass_eq_marginalYWMass_on_unit {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ]
    (P : FinitePMF (α × β × γ × Unit)) (y : β) :
    marginalYMass P y = marginalYWMass P (y, ()) := by
  unfold marginalYMass marginalYWMass
  simp

/-! ## KKT Certificate Structure -/

/--
A KKT certificate for the conditional mutual information I(Y; Z | W).

The certificate captures the sufficient KKT condition for capacity optimality:
if I(Y; Z | W) decomposes as Σ_y p_star(y) · per_symbol_I(y)
and each per_symbol_I(y) ≤ C, then I(Y; Z | W) ≤ C.
-/
structure KKT_Certificate
    {α β γ δ : Type}
    [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P4 : FinitePMF (α × β × γ × δ)) where
  C : ℝ
  p_star : β → ℝ
  per_symbol_I : β → ℝ
  h_weighted_decomp : I_YZ_W P4 = ∑ y : β, p_star y * per_symbol_I y
  h_kkt_condition : ∀ y : β, per_symbol_I y ≤ C
  h_p_star_nonneg : ∀ y : β, 0 ≤ p_star y
  h_p_star_sum_one : ∑ y : β, p_star y = 1

/--
Given a KKT certificate, I(Y; Z | W) ≤ C.

Proof: substitute the weighted decomposition, bound each term by C,
and simplify Σ p_star(y) = 1.
-/
theorem capacity_le_of_kkt
    {α β γ δ : Type}
    [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P4 : FinitePMF (α × β × γ × δ))
    (cert : KKT_Certificate P4) :
    I_YZ_W P4 ≤ cert.C := by
  calc
    I_YZ_W P4 = ∑ y : β, cert.p_star y * cert.per_symbol_I y := cert.h_weighted_decomp
    _ ≤ ∑ y : β, cert.p_star y * cert.C := by
      refine Finset.sum_le_sum (fun y _ => ?_)
      have hy_nonneg : 0 ≤ cert.p_star y := cert.h_p_star_nonneg y
      have hy_bound : cert.per_symbol_I y ≤ cert.C := cert.h_kkt_condition y
      exact mul_le_mul_of_nonneg_left hy_bound hy_nonneg
    _ = ∑ y : β, cert.C * cert.p_star y := by
      refine Finset.sum_congr rfl (fun y _ => ?_)
      ring
    _ = cert.C * (∑ y : β, cert.p_star y) := by rw [Finset.mul_sum]
    _ = cert.C * 1 := by rw [cert.h_p_star_sum_one]
    _ = cert.C := by ring

/-! ## Convenience: certificate from a direct bound -/

/--
Construct a KKT certificate from a direct bound on I_YZ_W and the actual
marginal distribution p(y) = marginalYMass(P4)(y).

The per-symbol terms are all set to I_YZ_W(P4), so the weighted decomposition
holds because Σ_y p(y) = 1.
-/
def KKT_Certificate.of_direct_bound
    {α β γ δ : Type}
    [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]
    (P4 : FinitePMF (α × β × γ × δ))
    (C : ℝ)
    (h_bound : I_YZ_W P4 ≤ C) : KKT_Certificate P4 :=
  {
    C := C
    p_star := marginalYMass P4
    per_symbol_I := fun _ => I_YZ_W P4
    h_weighted_decomp := by
      calc
        I_YZ_W P4 = (∑ y : β, marginalYMass P4 y) * I_YZ_W P4 := by
          rw [marginalYMass_sum_one P4, one_mul]
        _ = ∑ y : β, (marginalYMass P4 y * I_YZ_W P4) := by
          rw [Finset.sum_mul]
    h_kkt_condition := by
      intro y
      exact h_bound
    h_p_star_nonneg := marginalYMass_nonneg P4
    h_p_star_sum_one := marginalYMass_sum_one P4
  }

end
end FiniteQuerySandbox
