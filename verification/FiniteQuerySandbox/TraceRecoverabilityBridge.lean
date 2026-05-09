import FiniteQuerySandbox.ScreenabilityBridge

namespace FiniteQuerySandbox

/-!
# Trace Recoverability Bridge

Compatibility bridge re-export using non-paper terminology.
-/

/-- Bridge-level readable alias. -/
theorem no_internal_witness_trace_recoverability_bridge {Ω State Trace Action IState : Type}
    (screen : TraceRecoverability State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ¬ ExactInternalWitness S T A I chi :=
  no_internal_witness_under_trace_recoverability_bridge screen S T A h_screen chi I

end FiniteQuerySandbox
