import FiniteQuerySandbox.Screenability

namespace FiniteQuerySandbox

/-!
# Screenability Compatibility Bridge

Preferred reader-facing import: `FiniteQuerySandbox.TraceRecoverabilityBridge`.

The current paper no longer claims a separate EIS-to-zero-cut bridge theorem.
This module is retained only as a compatibility wrapper around the deterministic
autoregressive no-witness result used by older imports.
-/

/-- Compatibility wrapper for the deterministic autoregressive no-witness case. -/
theorem no_exact_witness_under_screen {Ω State Trace Action IState : Type}
    (screen : DeterministicScreen State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ¬ ExactEISWitness S T A I chi :=
  no_eis_autoregressive screen S T A h_screen chi I

/-- Bridge-level compatibility alias with non-paper terminology. -/
theorem no_internal_witness_under_trace_recoverability_bridge {Ω State Trace Action IState : Type}
    (screen : TraceRecoverability State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ¬ ExactInternalWitness S T A I chi :=
  no_internal_witness_under_trace_recoverability screen S T A h_screen chi I

end FiniteQuerySandbox
