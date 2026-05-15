import Mathlib
import FiniteQuerySandbox.InfoTheory

open Finset
open scoped BigOperators Real

namespace InfoTheory

open FiniteQuerySandbox

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

/-- 辅助引理：边缘分布的求和性质。 -/
lemma sum_marginalAC_eq_marginalC (P : FinitePMF (α × β × γ)) (c : γ) :
    ∑ a : α, (∑ b : β, P.pmf (a, b, c)) = (∑ a : α, ∑ b : β, P.pmf (a, b, c)) := by
  simp

/-- 条件互信息非负性的核心定理。 -/
theorem I_A_cond_B_C_nonneg (P : FinitePMF (α × β × γ)) :
    0 ≤ (entropyOf (fun ac : α × γ => ∑ b : β, P.pmf (ac.1, b, ac.2)) +
         entropyOf (fun bc : β × γ => ∑ a : α, P.pmf (a, bc.1, bc.2)) -
         entropyOf (fun c : γ => ∑ a : α, ∑ b : β, P.pmf (a, b, c)) -
         entropyOf (fun abc : α × β × γ => P.pmf abc)) := by
  simpa [FiniteQuerySandbox.condMutualInfo, FiniteQuerySandbox.marginalXZMass,
    FiniteQuerySandbox.marginalYZMass, FiniteQuerySandbox.marginalZMass] using
      (FiniteQuerySandbox.condMutualInfo_nonneg (P := P))

end InfoTheory
