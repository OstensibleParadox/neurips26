import Mathlib

namespace FiniteQuerySandbox

/-!
Preferred reader-facing import: `FiniteQuerySandbox.QuotientFactorization`.
-/

variable {E : Type*} [s : Setoid E]
variable (R : E → ℝ)

theorem semantic_closure_iff :
    (∀ e1 e2 : E, e1 ≈ e2 → R e1 = R e2) ↔
    (∃ R_bar : Quotient s → ℝ, ∀ e : E, R e = R_bar ⟦e⟧) := by
  constructor
  · intro h
    use Quotient.lift R h
    intro e
    rfl
  · rintro ⟨R_bar, h_bar⟩ e1 e2 h_eq
    rw [h_bar e1, h_bar e2, Quotient.sound h_eq]

/-- Compatibility alias: semantic closure is equivalent to factorization through
the quotient map induced by the setoid. -/
theorem factors_through_quotient_iff :
    (∀ e1 e2 : E, e1 ≈ e2 → R e1 = R e2) ↔
    (∃ R_bar : Quotient s → ℝ, ∀ e : E, R e = R_bar ⟦e⟧) :=
  semantic_closure_iff (R := R)

end FiniteQuerySandbox
