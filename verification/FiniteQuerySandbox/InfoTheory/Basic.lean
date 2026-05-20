import Mathlib

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

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

/-- The finite Shannon summand `-p log₂ p`. Mathlib's `Real.log 0 = 0` convention
makes the zero-mass term evaluate to zero. -/
def negMulLog2 (p : ℝ) : ℝ :=
  -(p * (Real.log p / Real.log 2))

end

end FiniteQuerySandbox
