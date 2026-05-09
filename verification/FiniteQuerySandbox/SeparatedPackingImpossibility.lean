import FiniteQuerySandbox.GeometricImpossibility

namespace FiniteQuerySandbox

/-!
# Separated-Packing Impossibility

Alias module for the geometric non-covering argument.
-/

variable {E H : Type*} [MetricSpace H]

/-- Readable alias for finite-support non-covering of a separated sequence. -/
theorem finite_support_cannot_cover_separated_sequence
    {eta : Nat → E} {hB : E → H} (gamma rho : ℝ) (h_rho : rho < gamma / 2)
    (h_sep : IsGammaSeparatedInjection eta hB gamma)
    (support : List Nat) :
    ∃ n : Nat, ∀ m ∈ support, dist (hB (eta n)) (hB (eta m)) > rho :=
  finite_patch_cannot_cover_separated gamma rho h_rho h_sep support

end FiniteQuerySandbox
