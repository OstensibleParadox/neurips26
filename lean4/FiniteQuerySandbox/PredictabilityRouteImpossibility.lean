import FiniteQuerySandbox.InternalImpossibility

namespace FiniteQuerySandbox

/-!
# Predictability-Route Impossibility

Alias module for the internal-route impossibility argument proved via
predictability surrogates.
-/

/-- Readable alias for the predictability-route impossibility theorem. -/
theorem internal_route_impossibility_predictability
    {Ω State Trace Action IState : Type*} [ps : ProbSpace Ω]
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (eps eps_min : ℝ) (h_bound : eps < eps_min)
    (h_screen : IsPredictable S T eps)
    (chi : State → IState) (I : Ω → IState) :
    ¬ IsEISWitness S T A I chi eps_min :=
  internal_impossibility_predictability S T A eps eps_min h_bound h_screen chi I

end FiniteQuerySandbox
