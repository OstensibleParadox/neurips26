import FiniteQuerySandbox.InfoTheory

namespace FiniteQuerySandbox

/-!
# Gap-Closing Certificates: Mechanized Information Theory Core

This module formalizes the structural reductions of Proposition 1 (Structural-Access
Closer) and Proposition 2 (Gray-Box-Access Closer). These correspond to the two
gap-closers of Theorem~1 (Output-Trace Identifiability Gap). Entropy and conditional
mutual information are the finite-discrete formulas from `InfoTheory.lean`;
conditional DPI is now discharged there from finite KL nonnegativity.
-/

noncomputable section

section DynamicCertificate

variable {Probe State Action Trace : Type}
variable [Fintype Probe] [Fintype State] [Fintype Action] [Fintype Trace]
variable [DecidableEq Probe] [DecidableEq State] [DecidableEq Action] [DecidableEq Trace]

/-- True residual decision relevance given the visible trace. -/
def delta_act (P : FinitePMF (Probe × State × Action × Trace)) : ℝ :=
  I_YZ_W P

/--
Proposition 2: Gray-Box-Access Closer (Conditional DPI).
Gap-closer for Theorem~1: if X_t is a probe variable satisfying the conditional
Markov chain X_t → S_t → A_t given T_tilde_t, then its conditional MI with A_t
lower-bounds delta_act, ruling out the P₀ (Dirac) realization.
-/
theorem prop2_dynamic_lb (P : FinitePMF (Probe × State × Action × Trace))
    (h_markov : condMarkov P) :
    I_XZ_W P ≤ delta_act P := by
  exact cond_dpi P h_markov

/--
Aggregated Dynamic Certificate.
Taking the maximum of several valid probe classes (e.g., replay, intervention, proxy)
yields a valid lower bound.
-/
theorem aggregated_dynamic_lb
    (P_replay : FinitePMF (Probe × State × Action × Trace))
    (P_interv : FinitePMF (Probe × State × Action × Trace))
    (P_proxy : FinitePMF (Probe × State × Action × Trace))
    (h1 : condMarkov P_replay)
    (h2 : condMarkov P_interv)
    (h3 : condMarkov P_proxy) :
    max (I_XZ_W P_replay)
        (max (I_XZ_W P_interv) (I_XZ_W P_proxy)) ≤
    max (delta_act P_replay)
        (max (delta_act P_interv) (delta_act P_proxy)) := by
  have hb1 := prop2_dynamic_lb P_replay h1
  have hb2 := prop2_dynamic_lb P_interv h2
  have hb3 := prop2_dynamic_lb P_proxy h3
  apply max_le
  · exact hb1.trans (le_max_left _ _)
  · apply max_le
    · exact hb2.trans (le_trans (le_max_left _ _) (le_max_right _ _))
    · exact hb3.trans (le_trans (le_max_right _ _) (le_max_right _ _))

end DynamicCertificate


section StaticCertificate

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

def stateVisibleMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (st : State × VisibleTrace) : ℝ :=
  ∑ m : MissingTrace, P.pmf (st.1, st.2, m)

def visibleMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (t : VisibleTrace) : ℝ :=
  ∑ s : State, ∑ m : MissingTrace, P.pmf (s, t, m)

def visibleMissingMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (tm : VisibleTrace × MissingTrace) : ℝ :=
  ∑ s : State, P.pmf (s, tm.1, tm.2)

def fullTraceEntropy (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (fun stm : State × VisibleTrace × MissingTrace => P.pmf stm)

/-- `H(S | T_tilde)`. -/
def H_S_cond_Ttilde (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (stateVisibleMass P) - entropyOf (visibleMass P)

/-- `H(S | T_full)`, where `T_full = (T_tilde, M)`. -/
def H_S_cond_Tfull (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  fullTraceEntropy P - entropyOf (visibleMissingMass P)

/-- `I(S; M | T_tilde)`. -/
def I_S_M_cond_Ttilde (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (stateVisibleMass P) +
    entropyOf (visibleMissingMass P) -
    entropyOf (visibleMass P) -
    fullTraceEntropy P

-- Theorem 1: TraceGap Chain Rule (was Axiom 3)
theorem chain_rule (P : FinitePMF (State × VisibleTrace × MissingTrace)) :
    H_S_cond_Ttilde P = H_S_cond_Tfull P + I_S_M_cond_Ttilde P := by
  unfold H_S_cond_Ttilde H_S_cond_Tfull I_S_M_cond_Ttilde fullTraceEntropy
  ring

/--
Software Orthogonality Hypothesis.
Assumes cut capacity is bounded by the sum of edge capacities.
Formulated as a predicate to keep the trusted external premise explicit.
-/
def software_orthogonal (Cut : Type) (C_cut : Cut → ℝ) (C_edge_sum : Cut → ℝ) (Cuts_U_to_S : Set Cut) : Prop :=
    ∀ Ω ∈ Cuts_U_to_S, C_cut Ω ≤ C_edge_sum Ω

/--
Proposition 1: Structural-Access Closer (Static Cut-Sum Bound).
Gap-closer for Theorem~1: under structural access with full logging,
ε_state^UB = 0 collapses both realizations to a single equivalence class.

Note: The premise `h_bound` will be discharged by the cut-set bound
(network info theory) when the full DPI infrastructure is in place.
-/
theorem prop1_static_ub
    (Cut : Type) (C_cut : Cut → ℝ)
    (Ω : Cut)
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (h_bound : I_S_M_cond_Ttilde P ≤ C_cut Ω) :
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_cut Ω := by
  have h_chain := chain_rule P
  rw [h_chain]
  exact add_le_add (le_refl (H_S_cond_Tfull P)) h_bound

/-- Edge-additive form (Corollary) -/
theorem corollary_additive_ub
    (Cut : Type) (C_cut : Cut → ℝ) (C_edge_sum : Cut → ℝ) (Cuts_U_to_S : Set Cut)
    (Ω : Cut) (hΩ : Ω ∈ Cuts_U_to_S)
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (h_bound : I_S_M_cond_Ttilde P ≤ C_cut Ω)
    (h_ortho : software_orthogonal Cut C_cut C_edge_sum Cuts_U_to_S) :
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_edge_sum Ω := by
  have h_prop1 := prop1_static_ub Cut C_cut Ω P h_bound
  have h_ortho_bound : C_cut Ω ≤ C_edge_sum Ω := h_ortho Ω hΩ
  calc
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_cut Ω := h_prop1
    _ ≤ H_S_cond_Tfull P + C_edge_sum Ω := add_le_add (le_refl (H_S_cond_Tfull P)) h_ortho_bound

end StaticCertificate

end

end FiniteQuerySandbox
