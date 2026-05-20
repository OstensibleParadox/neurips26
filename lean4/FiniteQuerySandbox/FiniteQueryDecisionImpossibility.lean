import FiniteQuerySandbox.Impossibility

namespace FiniteQuerySandbox

/-!
# Finite-Query Decision Impossibility

Alias module for the finite-query certifier impossibility result.
-/

/-- Readable alias for the finite-query soundness/completeness impossibility. -/
theorem finite_query_decision_impossibility (C : FiniteQueryCertifier) :
    ¬ (Sound C ∧ Complete C) :=
  finite_query_impossibility C

end FiniteQuerySandbox
