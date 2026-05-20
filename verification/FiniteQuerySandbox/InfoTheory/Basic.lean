import Mathlib

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

/-- A finite discrete probability mass function over type `α`. -/
structure FinitePMF (α : Type) [Fintype α] [DecidableEq α] where
  pmf : α → ℝ
  pmf_nonneg : ∀ x, 0 ≤ pmf x
  sum_one : ∑ x : α, pmf x = 1

def FinitePMF.comapEquiv {η θ : Type} [Fintype η] [DecidableEq η] [Fintype θ]
    [DecidableEq θ] (e : θ ≃ η) (P : FinitePMF η) : FinitePMF θ where
  pmf x := P.pmf (e x)
  pmf_nonneg x := P.pmf_nonneg (e x)
  sum_one := by
    calc
      ∑ x : θ, P.pmf (e x) = ∑ y : η, P.pmf y := Equiv.sum_comp e P.pmf
      _ = 1 := P.sum_one

/--
Unified distribution pushforward (map).
Given P : FinitePMF α and function f : α → β, constructs a distribution on β.
Conservation of mass guaranteed by Finset.sum_comm.
-/
def FinitePMF.map
    {α β : Type} [Fintype α] [DecidableEq α] [Fintype β] [DecidableEq β]
    (P : FinitePMF α) (f : α → β) : FinitePMF β where
  pmf y := ∑ x : α, if f x = y then P.pmf x else 0
  pmf_nonneg y := by
    apply Finset.sum_nonneg
    intro x _
    by_cases h : f x = y
    · simp [h, P.pmf_nonneg x]
    · simp [h]
  sum_one := by
    calc
      ∑ y : β, ∑ x : α, (if f x = y then P.pmf x else 0)
          = ∑ x : α, ∑ y : β, (if f x = y then P.pmf x else 0) := by
            exact Finset.sum_comm
      _ = ∑ x : α, P.pmf x := by
        apply Finset.sum_congr rfl
        intro x _
        calc
          ∑ y : β, (if f x = y then P.pmf x else 0)
              = P.pmf x * ∑ y : β, (if f x = y then (1 : ℝ) else 0) := by
                  rw [Finset.mul_sum]
                  apply Finset.sum_congr rfl
                  intro y _
                  by_cases h : f x = y
                  · simp [h]
                  · simp [h]
          _ = P.pmf x := by simp
      _ = 1 := P.sum_one

end

end FiniteQuerySandbox
