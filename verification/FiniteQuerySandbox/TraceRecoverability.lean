import FiniteQuerySandbox.Screenability

namespace FiniteQuerySandbox

/-!
# Trace Recoverability

Reader-facing entry point for the deterministic trace-to-state recoverability
core (paper term: screenability).
-/

/-- Readable alias for the exact-core impossibility theorem. -/
theorem no_internal_witness_trace_recoverability {Ω State Trace Action IState : Type}
    (screen : TraceRecoverability State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ¬ ExactInternalWitness S T A I chi :=
  no_internal_witness_under_trace_recoverability screen S T A h_screen chi I

end FiniteQuerySandbox
