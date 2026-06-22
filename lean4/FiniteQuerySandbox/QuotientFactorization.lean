import FiniteQuerySandbox.SemanticClosureIff

namespace FiniteQuerySandbox

/-!
# Quotient Factorization

Reader-facing alias module for the semantic-closure/factorization equivalence.
-/

/-- Readable alias to the semantic-closure equivalence theorem. -/
theorem semantic_factorization_iff {E : Type*} [s : Setoid E] (R : E → ℝ) :
    (∀ e1 e2 : E, e1 ≈ e2 → R e1 = R e2) ↔
    (∃ R_bar : Quotient s → ℝ, ∀ e : E, R e = R_bar ⟦e⟧) :=
  factors_through_quotient_iff (R := R)

end FiniteQuerySandbox
