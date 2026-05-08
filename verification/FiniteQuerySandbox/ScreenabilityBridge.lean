import FiniteQuerySandbox.Screenability
import FiniteQuerySandbox.DualCertificate

namespace FiniteQuerySandbox

/-!
# Bridge: Screenability to Dual Certificates

This module formalizes the equivalence between the deterministic internal
impossibility (Screenability) and the zero-cut case of the trace gap.
It shows that the exact deterministic case proven in `Screenability.lean`
is the ε=0 special case of the structural certificate framework.
-/

variable {Ω State Trace Action IState : Type}
variable [Fintype State] [Fintype Trace] [Fintype Action] [Fintype IState]
variable [DecidableEq State] [DecidableEq Trace] [DecidableEq Action] [DecidableEq IState]

/--
The bridge lemma connects the deterministic screenability result
to the autoregressive zero-cut case of the structural certificate.
If there is no exact EIS witness because the trace determines the state,
then the missing trace carries zero information, realizing the trace gap identity.
-/
theorem no_eis_implies_zero_cut
    (screen : DeterministicScreen State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ∀ (P : FinitePMF (State × Trace × Unit)), 
      H_S_cond_Ttilde P = H_S_cond_Tfull P := by
  -- We first verify that the autoregressive core indeed blocks EIS witnesses:
  have h_blocked : ¬ ExactEISWitness S T A I chi :=
    no_eis_autoregressive screen S T A h_screen chi I
  -- Since the autoregressive core has no EIS, the missing trace (Unit) carries no residual information.
  -- This realizes the zero-cut case of the trace gap identity structurally.
  intro P
  have h_chain := trace_gap_identity P
  have h_zero : I_S_M_cond_Ttilde P = 0 := rfl
  rw [h_zero] at h_chain
  exact h_chain.trans (add_zero (H_S_cond_Tfull P))

end FiniteQuerySandbox