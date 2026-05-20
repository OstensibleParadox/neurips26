import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Basic

namespace FiniteQuerySandbox

/-!
# Predictability-based Screenability (Internal Route)

Preferred reader-facing import:
`FiniteQuerySandbox.PredictabilityRouteImpossibility`.

This module formalizes the internal route impossibility using predictability
as an operational surrogate for information-theoretic entropy conditions.

As with the paper's decision to leave the Gaussian-KL / Fano layer external in
the PAC argument, this file leaves the full entropy / conditional-mutual-
information development outside the Lean artifact and checks the proof skeleton
at the lighter predictability level instead.

## Relationship to paper Definition 1 (EIS)

The paper defines an EIS witness via three conditions on I_t = χ(S_t):
  (1) endogeneity  — I factors through the full operative state
  (2) residual autonomy  — H(I_t | T_t) > 0
  (3) decision relevance — I(I_t ; A_t | T_t) > 0

This module operationalizes (2) and (3) with finite surrogates:
  (2') I cannot be predicted from T within error eps_min
  (3') same-trace covariation: ∃ ω₁ ω₂, T ω₁ = T ω₂ ∧ I ω₁ ≠ I ω₂ ∧ A ω₁ ≠ A ω₂

These surrogates are strictly weaker than the information-theoretic originals.
In particular, (3') captures same-trace covariation of I and A but does NOT
formalize causal influence or conditional mutual information. See field-level
comments in `IsEISWitness` for details.
-/

/-- Minimal probability-space interface: a normalized, monotone set function.

This is NOT a σ-additive measure; it lacks countable additivity, null-set
structure, and measurability constraints. The proofs in this module only
require monotonicity (`prob_mono`) and normalization (`prob_univ`), so the
weaker interface suffices for the algebraic argument. However, `prob` should
not be read as carrying full measure-theoretic probability semantics. -/
class ProbSpace (Ω : Type*) where
  prob : Set Ω → ℝ
  prob_nonneg : ∀ s, 0 ≤ prob s
  prob_univ : prob Set.univ = 1
  prob_mono : ∀ {s t : Set Ω}, s ⊆ t → prob s ≤ prob t

/--
S is eps-predictable from T if there exists a predictor hat_S such that
`prob {ω | hat_S (T ω) ≠ S ω} ≤ eps`. Under a genuine probability
measure this is prediction-error probability; under our minimal `ProbSpace`
interface it is a normalized monotone bound. The proofs use only
monotonicity, so the distinction does not affect correctness.
-/
def IsPredictable {Ω State Trace : Type*} [ps : ProbSpace Ω]
    (S : Ω → State) (T : Ω → Trace) (eps : ℝ) : Prop :=
  ∃ hat_S : Trace → State, ps.prob {ω | hat_S (T ω) ≠ S ω} ≤ eps

/--
EIS witness predicate (operational version of paper Definition 1).

The paper's EIS witness requires three conditions on an admissible
internal-state candidate I_t = χ(S_t). This structure formalizes all
three using operational surrogates for the information-theoretic
conditions. The projection χ maps from the full operative state type
to a potentially different internal-state type IState, matching the
paper's generality.

**Surrogates used:**
- `residual_autonomy`: unpredictability of I from T (surrogate for H(I|T) > 0)
- `decision_relevance`: same-trace covariation of I and A (surrogate for I(I;A|T) > 0)

Neither surrogate is equivalent to the information-theoretic original.
See field-level comments.
-/
structure IsEISWitness {Ω State Trace Action IState : Type*} [ps : ProbSpace Ω]
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (I : Ω → IState) (chi : State → IState) (eps_min : ℝ) : Prop where
  /-- Endogeneity: I factors through the full operative state via projection χ.
      Matches paper Definition 1 condition (1) exactly. -/
  endogeneity : ∀ ω, I ω = chi (S ω)
  /-- Residual autonomy (predictability surrogate for H(I_t | T_t) > 0).
      The paper requires strictly positive conditional entropy of I given T.
      We operationalize this as: I cannot be predicted from T with error
      bounded by eps_min. This is a sufficient but not necessary condition
      for H(I|T) > 0 in general; the relationship is exact only in
      degenerate cases. -/
  residual_autonomy : ¬ IsPredictable I T eps_min
  /-- Decision relevance (same-trace covariation surrogate for I(I_t ; A_t | T_t) > 0).
      The paper requires strictly positive conditional mutual information
      between I and A given T, i.e., knowing I provides information about
      the action beyond what the trace already determines.

      This surrogate is strictly weaker: it only requires that there exist
      two outcomes sharing the same trace value where I and A both differ.
      This captures same-trace covariation but does NOT formalize causal
      influence or conditional mutual information. In particular, I and A
      could covary for unrelated reasons (confounding) and this condition
      would still hold. It is a necessary condition for I(I;A|T) > 0 in
      finite discrete settings, but not sufficient.

      The impossibility proof does not depend on this field — it contradicts
      residual_autonomy directly. This field is included for definitional
      completeness: without it, the structure would not reflect the paper's
      three-part EIS definition, and Action would be a dead parameter. -/
  decision_relevance : ∃ ω₁ ω₂ : Ω, T ω₁ = T ω₂ ∧ I ω₁ ≠ I ω₂ ∧ A ω₁ ≠ A ω₂

/--
Lemma 1 (Full-State Screenability Lemma, predictability version):
If the full state S is predictable from the trace T with error at most eps,
then any admissible projection χ(S) is also predictable with the same
error bound. This is the data-processing step.
-/
lemma screenability_lemma_predictability
    {Ω State Trace IState : Type*} [ps : ProbSpace Ω]
    (S : Ω → State) (T : Ω → Trace) (eps : ℝ) (chi : State → IState)
    (hS : IsPredictable S T eps) :
    IsPredictable (fun ω => chi (S ω)) T eps := by
  rcases hS with ⟨hat_S, h_err⟩
  let hat_I : Trace → IState := fun t => chi (hat_S t)
  use hat_I
  have h_subset :
      {ω | hat_I (T ω) ≠ chi (S ω)}
        ⊆ {ω | hat_S (T ω) ≠ S ω} := by
    intro ω h_bad h_good
    exact h_bad (by simp [hat_I, h_good])
  exact le_trans (ps.prob_mono h_subset) h_err

/--
Internal route impossibility (predictability version of paper Corollary 2).

Under ε-screenability (the full state S is predictable from T at error eps),
no admissible projection I = χ(S) can satisfy all three operational
EIS-witness conditions when eps < eps_min. The proof contradicts the
residual_autonomy condition
specifically: screenability propagates through the projection (by the
screenability lemma), making I predictable at error eps, which is below
the eps_min threshold required for residual autonomy.

The decision_relevance field is present in IsEISWitness for definitional
fidelity but is not needed for this impossibility — failing any one of
the three operational conditions suffices to block EIS-witness status.
-/
theorem internal_impossibility_predictability
    {Ω State Trace Action IState : Type*} [ps : ProbSpace Ω]
    (S : Ω → State) (T : Ω → Trace) (A : Ω → Action)
    (eps eps_min : ℝ) (h_bound : eps < eps_min)
    (h_screen : IsPredictable S T eps)
    (chi : State → IState) (I : Ω → IState) :
    ¬ IsEISWitness S T A I chi eps_min := by
  intro hEIS
  have h_autonomy := hEIS.residual_autonomy
  have h_I_pred : IsPredictable I T eps := by
    have h_eq : I = (fun ω => chi (S ω)) := funext hEIS.endogeneity
    rw [h_eq]
    exact screenability_lemma_predictability S T eps chi h_screen
  have h_I_pred_min : IsPredictable I T eps_min := by
    rcases h_I_pred with ⟨hat_I, h_err⟩
    use hat_I
    exact le_trans h_err (le_of_lt h_bound)
  exact h_autonomy h_I_pred_min

end FiniteQuerySandbox
