namespace FiniteQuerySandbox

/-!
# Deterministic Screenability (ε = 0)

Preferred reader-facing import: `FiniteQuerySandbox.TraceRecoverability`.
This module is retained as the canonical paper-term entry point.

This module formalizes the autoregressive core case of the internal route:
when the full endogenous operative state S_t is a deterministic function of
the audit trace T_t, no admissible projection χ(S_t) retains residual
autonomy.

This corresponds to Corollary 2 of the paper. The ε > 0 (wrapper) case
is handled in `InternalImpossibility.lean` using predictability.

The formalization deliberately stops at exact same-trace surrogates rather
than building the full entropy / conditional-mutual-information machinery.
The obstruction already appears at this exact discrete level, and the heavier
information-theoretic development is treated in the paper the same way that
the external Fano / Gaussian-KL layer is treated: as mathematically standard
but outside the scope of this Lean supplement.

## Paper-to-Lean Map

- exact deterministic-screenability core of Lemma 1 → `projection_determined`
- exact same-trace witness surrogate for Definition 1 (EIS) → `ExactEISWitness`
- exact-core no-witness corollary for autoregressive cores → `no_eis_autoregressive`
-/

/--
A deterministic screen captures the ε = 0 case of full-state screenability:
the full endogenous operative state `S` is a deterministic function of the
audit trace `T`. This models the autoregressive core graph where
S_t = f(X_t) and T_t = X_t.
-/
structure DeterministicScreen (S : Type) (T : Type) where
  /-- Reconstruction: the audit trace determines the full operative state. -/
  recon : T → S

/-- Compatibility alias: deterministic trace recoverability of the operative state. -/
abbrev TraceRecoverability (S : Type) (T : Type) := DeterministicScreen S T

/--
Lemma 1 at ε = 0: if S is determined by T, then any projection χ(S)
is also determined by T. This is the data-processing step that blocks
residual autonomy for every admissible candidate I_t = χ(S_t).
-/
theorem projection_determined {S T I : Type}
    (screen : DeterministicScreen S T) (χ : S → I) :
    ∃ recon_I : T → I, ∀ t, recon_I t = χ (screen.recon t) :=
  ⟨χ ∘ screen.recon, fun _ => rfl⟩

/--
Deterministic screenability makes the projected state χ(S) constant on
trace-equivalent outcomes. This is the exact ε = 0 surrogate for the
paper's entropy-based residual-autonomy step.
-/
theorem projection_same_trace_eq {Ω State Trace IState : Type}
    (screen : DeterministicScreen State Trace)
    (S : Ω → State) (T : Ω → Trace)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) :
    ∀ ω₁ ω₂, T ω₁ = T ω₂ → chi (S ω₁) = chi (S ω₂) := by
  intro ω₁ ω₂ hT
  calc
    chi (S ω₁) = chi (screen.recon (T ω₁)) := by rw [h_screen ω₁]
    _ = chi (screen.recon (T ω₂)) := by rw [hT]
    _ = chi (S ω₂) := by rw [h_screen ω₂]

/--
Residual autonomy surrogate is impossible once S is deterministically
screened by T and the internal candidate is an admissible projection of S.
This is the direct same-trace-variation obstruction used in the exact core.
-/
theorem no_same_trace_projection_variation {Ω State Trace IState : Type}
    (screen : DeterministicScreen State Trace)
    (S : Ω → State) (T : Ω → Trace)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) :
    ¬ ∃ ω₁ ω₂ : Ω, T ω₁ = T ω₂ ∧ chi (S ω₁) ≠ chi (S ω₂) := by
  intro h
  rcases h with ⟨ω₁, ω₂, hT, hneq⟩
  exact hneq (projection_same_trace_eq screen S T h_screen chi ω₁ ω₂ hT)

/--
Decision-relevance surrogate is also blocked at the exact core:
if χ(S) is trace-determined, then there can be no same-trace witness with
both differing internal state and differing action.
-/
theorem no_same_trace_IA_witness {Ω State Trace Action IState : Type}
    (screen : DeterministicScreen State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) :
    ¬ ∃ ω₁ ω₂ : Ω, T ω₁ = T ω₂ ∧ chi (S ω₁) ≠ chi (S ω₂) ∧ A ω₁ ≠ A ω₂ := by
  intro h
  rcases h with ⟨ω₁, ω₂, hT, hI, _hA⟩
  exact hI (projection_same_trace_eq screen S T h_screen chi ω₁ ω₂ hT)

/--
Exact internal-state witness predicate (operational version of paper Definition 1 for ε = 0).

This structure matches the three conditions of an EIS witness using exact surrogates
over an outcome type Ω.
-/
structure ExactEISWitness {Ω State Trace Action IState : Type}
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (I : Ω → IState) (chi : State → IState) : Prop where
  /-- Endogeneity: I factors through the full operative state via projection χ. -/
  endogeneity : ∀ ω, I ω = chi (S ω)
  /-- Residual autonomy surrogate (ε = 0 case): there exist outcomes with the same trace but different internal-state value. -/
  residual_autonomy : ∃ ω₁ ω₂ : Ω, T ω₁ = T ω₂ ∧ I ω₁ ≠ I ω₂
  /-- Decision relevance surrogate: same-trace covariation of I and A. -/
  decision_relevance : ∃ ω₁ ω₂ : Ω, T ω₁ = T ω₂ ∧ I ω₁ ≠ I ω₂ ∧ A ω₁ ≠ A ω₂

/-- Compatibility alias for readers outside the paper's EIS terminology. -/
abbrev ExactInternalWitness {Ω State Trace Action IState : Type}
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (I : Ω → IState) (chi : State → IState) : Prop :=
  ExactEISWitness S T A I chi

/--
Corollary 1: Under a deterministic screen (autoregressive core),
no admissible projection χ(S_t) can be an exact internal-state witness.
Deterministic screenability of S from T blocks any endogenous candidate I = χ(S)
from having same-trace residual variation.
-/
theorem no_eis_autoregressive {Ω State Trace Action IState : Type}
    (screen : DeterministicScreen State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ¬ ExactEISWitness S T A I chi := by
  intro h
  have h_no_var := no_same_trace_projection_variation screen S T h_screen chi
  rcases h.residual_autonomy with ⟨ω₁, ω₂, hT, hI⟩
  apply h_no_var
  exact ⟨ω₁, ω₂, hT, by
    intro h_eq
    apply hI
    rw [h.endogeneity ω₁, h.endogeneity ω₂]
    exact h_eq⟩

/-- Compatibility alias for non-paper terminology. -/
theorem no_internal_witness_under_trace_recoverability {Ω State Trace Action IState : Type}
    (screen : TraceRecoverability State Trace)
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (h_screen : ∀ ω, S ω = screen.recon (T ω))
    (chi : State → IState) (I : Ω → IState) :
    ¬ ExactInternalWitness S T A I chi :=
  no_eis_autoregressive screen S T A h_screen chi I

/--
Composition: if two deterministic screens compose (T determines S,
S determines U), then T determines U. This models the Markov chain
T_t → S_t → I_t.
-/
theorem screen_compose {S T U : Type}
    (screen_ST : DeterministicScreen S T)
    (screen_SU : DeterministicScreen U S) :
    ∃ recon_TU : T → U, ∀ t, recon_TU t = screen_SU.recon (screen_ST.recon t) :=
  ⟨screen_SU.recon ∘ screen_ST.recon, fun _ => rfl⟩

/-- Example: the identity screen (S = T) trivially satisfies determinism. -/
def identityScreen (T : Type) : DeterministicScreen T T where
  recon := id

/-- Example: composing a projection with the identity screen. -/
example {T I : Type} (χ : T → I) :
    ∃ recon_I : T → I, ∀ t, recon_I t = χ ((identityScreen T).recon t) :=
  projection_determined (identityScreen T) χ

end FiniteQuerySandbox
