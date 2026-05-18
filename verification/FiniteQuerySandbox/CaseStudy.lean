import Mathlib
import FiniteQuerySandbox.InfoTheory
import FiniteQuerySandbox.ChannelCapacity
import FiniteQuerySandbox.MarkovGenerator
import CutSetBoundExtract

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

section Types

abbrev State2 := Fin 2
abbrev CutVar2 := Fin 2
abbrev Missing2 := Fin 2

end Types

section UnitLemmas

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

lemma negMulLog2_one : negMulLog2 (1 : ℝ) = 0 := by
  unfold negMulLog2; simp

lemma h_total_one (P4 : FinitePMF (α × β × γ × Unit)) :
    ∑ x : α, ∑ y : β, ∑ z : γ, P4.pmf (x, y, z, ()) = 1 := by
  let e : α × β × γ ≃ α × β × γ × Unit := {
    toFun := fun xyz => (xyz.1, xyz.2.1, xyz.2.2, ())
    invFun := fun xyzw => (xyzw.1, xyzw.2.1, xyzw.2.2.1)
    left_inv := by intro xyz; rfl
    right_inv := by intro xyzw; simp
  }
  calc
    ∑ x : α, ∑ y : β, ∑ z : γ, P4.pmf (x, y, z, ())
        = ∑ p : (α × β × γ), P4.pmf (p.1, p.2.1, p.2.2, ()) := by
      simp [Fintype.sum_prod_type]
    _ = ∑ p : (α × β × γ), P4.pmf (e p) := rfl
    _ = ∑ p : (α × β × γ × Unit), P4.pmf p := Equiv.sum_comp e (P4.pmf)
    _ = 1 := P4.sum_one

lemma marginalWMass_unit_one (P4 : FinitePMF (α × β × γ × Unit)) :
    marginalWMass P4 = fun (_ : Unit) => 1 := by
  funext w; cases w
  unfold marginalWMass
  simpa using h_total_one P4

lemma entropyOf_marginalWMass_unit_zero (P4 : FinitePMF (α × β × γ × Unit)) :
    entropyOf (marginalWMass P4) = 0 := by
  rw [marginalWMass_unit_one P4, entropyOf]
  simp [negMulLog2_one]

def marginalZMass_unit (P4 : FinitePMF (α × β × γ × Unit)) (z : γ) : ℝ :=
  ∑ x : α, ∑ y : β, P4.pmf (x, y, z, ())

lemma marginalZMass_unit_nonneg (P4 : FinitePMF (α × β × γ × Unit)) (z : γ) :
    0 ≤ marginalZMass_unit P4 z := by
  unfold marginalZMass_unit
  apply Finset.sum_nonneg; intro x _
  apply Finset.sum_nonneg; intro y _
  exact P4.pmf_nonneg (x, y, z, ())

lemma marginalZMass_unit_sum_one (P4 : FinitePMF (α × β × γ × Unit)) :
    ∑ z : γ, marginalZMass_unit P4 z = 1 := by
  unfold marginalZMass_unit
  have h1 : ∑ z : γ, ∑ x : α, ∑ y : β, P4.pmf (x, y, z, ()) =
    ∑ p : γ × α, ∑ y : β, P4.pmf (p.2, y, p.1, ()) := by
    rw [← Fintype.sum_prod_type (f := fun (zx : γ × α) => ∑ y : β, P4.pmf (zx.2, y, zx.1, ()))]
  have h2 : ∑ p : γ × α, ∑ y : β, P4.pmf (p.2, y, p.1, ()) =
    ∑ q : (γ × α) × β, P4.pmf (q.1.2, q.2, q.1.1, ()) := by
    rw [← Fintype.sum_prod_type (f := fun (py : (γ × α) × β) => P4.pmf (py.1.2, py.2, py.1.1, ()))]
  rw [h1, h2]
  let e : (γ × α) × β ≃ α × β × γ × Unit := {
    toFun := fun q => (q.1.2, q.2, q.1.1, ())
    invFun := fun xyzw => ((xyzw.2.2.1, xyzw.1), xyzw.2.1)
    left_inv := by intro q; simp
    right_inv := by intro xyzw; simp
  }
  calc
    ∑ q : ((γ × α) × β), P4.pmf (q.1.2, q.2, q.1.1, ())
        = ∑ q : ((γ × α) × β), P4.pmf (e q) := rfl
    _ = ∑ p : (α × β × γ × Unit), P4.pmf p := Equiv.sum_comp e (P4.pmf)
    _ = 1 := P4.sum_one

/-- (Y,Z) marginal PMF when W = Unit. -/
def marginalYZPMF_of_unit (P4 : FinitePMF (α × β × γ × Unit)) : FinitePMF (β × γ) where
  pmf yz := ∑ x : α, P4.pmf (x, yz.1, yz.2, ())
  pmf_nonneg := by
    intro yz; apply Finset.sum_nonneg; intro x _
    exact P4.pmf_nonneg (x, yz.1, yz.2, ())
  sum_one := by
    calc
      ∑ yz : β × γ, ∑ x : α, P4.pmf (x, yz.1, yz.2, ())
          = ∑ x : α, ∑ yz : β × γ, P4.pmf (x, yz.1, yz.2, ()) := by
        rw [Finset.sum_comm]
      _ = ∑ x : α, ∑ y : β, ∑ z : γ, P4.pmf (x, y, z, ()) := by
        simp [Fintype.sum_prod_type]
      _ = 1 := h_total_one P4

lemma marginalYZWMass_eq_marginalYZPMF_of_unit_pmf
    (P4 : FinitePMF (α × β × γ × Unit)) (y : β) (z : γ) :
    marginalYZWMass P4 (y, z, ()) = (marginalYZPMF_of_unit P4).pmf (y, z) := by
  unfold marginalYZPMF_of_unit marginalYZWMass; simp

lemma marginalZWMass_eq_marginalZMass_unit
    (P4 : FinitePMF (α × β × γ × Unit)) (z : γ) :
    marginalZWMass P4 (z, ()) = marginalZMass_unit P4 z := by
  unfold marginalZWMass marginalZMass_unit; simp

lemma marginalYWMass_eq_marginalYMass (P4 : FinitePMF (α × β × γ × Unit)) (y : β) :
    marginalYWMass P4 (y, ()) = marginalYMass P4 y := by
  unfold marginalYWMass marginalYMass; simp

lemma entropyOf_marginalYWMass_eq_entropyOf_marginalYMass
    (P4 : FinitePMF (α × β × γ × Unit)) :
    entropyOf (marginalYWMass P4) = entropyOf (marginalYMass P4) := by
  let e : β × Unit ≃ β := {
    toFun := fun yw => yw.1
    invFun := fun y => (y, ())
    left_inv := by intro yw; cases yw; rfl
    right_inv := by intro y; rfl
  }
  have h_eq : ∀ yw : β × Unit, marginalYWMass P4 yw = marginalYMass P4 (e yw) := by
    intro yw
    have h_un : yw = (yw.1, ()) := by
      ext; simp
    calc
      marginalYWMass P4 yw = marginalYWMass P4 (yw.1, ()) := by rw [h_un]
      _ = marginalYMass P4 yw.1 := marginalYWMass_eq_marginalYMass P4 yw.1
      _ = marginalYMass P4 (e yw) := by simp [e]
  exact entropyOf_equiv_eq e (marginalYWMass P4) (marginalYMass P4) h_eq

lemma entropyOf_marginalZWMass_eq_entropyOf_marginalZMass_unit
    (P4 : FinitePMF (α × β × γ × Unit)) :
    entropyOf (marginalZWMass P4) = entropyOf (marginalZMass_unit P4) := by
  let e : γ × Unit ≃ γ := {
    toFun := fun zw => zw.1
    invFun := fun z => (z, ())
    left_inv := by intro zw; cases zw; rfl
    right_inv := by intro z; rfl
  }
  have h_eq : ∀ zw : γ × Unit, marginalZWMass P4 zw = marginalZMass_unit P4 (e zw) := by
    intro zw
    have h_un : zw = (zw.1, ()) := by
      ext; simp
    calc
      marginalZWMass P4 zw = marginalZWMass P4 (zw.1, ()) := by rw [h_un]
      _ = marginalZMass_unit P4 zw.1 := marginalZWMass_eq_marginalZMass_unit P4 zw.1
      _ = marginalZMass_unit P4 (e zw) := by simp [e]
  exact entropyOf_equiv_eq e (marginalZWMass P4) (marginalZMass_unit P4) h_eq

lemma entropyOf_marginalYZWMass_eq_entropyOf_marginalYZPMF
    (P4 : FinitePMF (α × β × γ × Unit)) :
    entropyOf (marginalYZWMass P4) = entropyOf ((marginalYZPMF_of_unit P4).pmf) := by
  let e : (β × γ × Unit) ≃ β × γ := {
    toFun := fun yzw => (yzw.1, yzw.2.1)
    invFun := fun yz => (yz.1, yz.2, ())
    left_inv := by intro yzw; cases yzw; rfl
    right_inv := by intro yz; cases yz; rfl
  }
  have h_eq : ∀ yzw : β × γ × Unit, marginalYZWMass P4 yzw = (marginalYZPMF_of_unit P4).pmf (e yzw) := by
    intro yzw
    have h_un : yzw = (yzw.1, yzw.2.1, ()) := by
      cases yzw; rename_i y z w; cases w; rfl
    calc
      marginalYZWMass P4 yzw = marginalYZWMass P4 (yzw.1, yzw.2.1, ()) := by rw [h_un]
      _ = (marginalYZPMF_of_unit P4).pmf (yzw.1, yzw.2.1) :=
        marginalYZWMass_eq_marginalYZPMF_of_unit_pmf P4 yzw.1 yzw.2.1
      _ = (marginalYZPMF_of_unit P4).pmf (e yzw) := by simp [e]
  exact entropyOf_equiv_eq e (marginalYZWMass P4) ((marginalYZPMF_of_unit P4).pmf) h_eq

lemma I_YZ_W_unit_le_entropyOf_marginalYMass (P4 : FinitePMF (α × β × γ × Unit)) :
    I_YZ_W P4 ≤ entropyOf (marginalYMass P4) := by
  unfold I_YZ_W
  have hW : entropyOf (marginalWMass P4) = 0 := entropyOf_marginalWMass_unit_zero P4
  have hYW : entropyOf (marginalYWMass P4) = entropyOf (marginalYMass P4) :=
    entropyOf_marginalYWMass_eq_entropyOf_marginalYMass P4
  have hZW : entropyOf (marginalZWMass P4) = entropyOf (marginalZMass_unit P4) :=
    entropyOf_marginalZWMass_eq_entropyOf_marginalZMass_unit P4
  have hYZW : entropyOf (marginalYZWMass P4) = entropyOf ((marginalYZPMF_of_unit P4).pmf) :=
    entropyOf_marginalYZWMass_eq_entropyOf_marginalYZPMF P4
  rw [hW, hYW, hZW, hYZW, sub_zero]
  let Q := marginalYZPMF_of_unit P4
  have h_cond_nonneg : 0 ≤ condEntropy Q := condEntropy_nonneg Q
  unfold condEntropy at h_cond_nonneg
  have h_margRight : marginalRightMass Q = marginalZMass_unit P4 := by
    funext z
    unfold marginalRightMass Q marginalYZPMF_of_unit marginalZMass_unit
    rw [Finset.sum_comm]
  rw [h_margRight] at h_cond_nonneg
  linarith

lemma I_YZ_W_unit_CutVar2_le_one
    {α : Type} [Fintype α] [DecidableEq α]
    (P4 : FinitePMF (α × CutVar2 × Missing2 × Unit)) :
    I_YZ_W P4 ≤ 1 := by
  have h_Y_entropy_bound : entropyOf (marginalYMass P4) ≤ 1 := by
    let Q : FinitePMF CutVar2 := {
      pmf := marginalYMass P4
      pmf_nonneg := marginalYMass_nonneg P4
      sum_one := marginalYMass_sum_one P4
    }
    have hQ := entropy_le_log_card Q
    have card2 : Fintype.card CutVar2 = 2 := by decide
    have h_card : Real.log (Fintype.card CutVar2 : ℝ) / Real.log 2 = 1 := by
      have hlog2_pos : Real.log (2 : ℝ) > 0 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
      simp [card2, hlog2_pos.ne']
    have h_entropy_eq : entropy Q = entropyOf (marginalYMass P4) := rfl
    rw [h_entropy_eq, h_card] at hQ
    exact hQ
  have h_YZ_W_le_HY := I_YZ_W_unit_le_entropyOf_marginalYMass P4
  linarith

/--
If S and M are independent under P (when the visible trace T = Unit) and Ω_vars
depends only on S (not on the missing trace M), then the pushforward
P4 = pmf_from_vars P Ω_vars satisfies the condMarkov property. This means the
cut variable Y = Ω(S,T,M) separates S from M, forming the chain S → Y → M.

The independence condition P(S=s, T=(), M=m) = P_S(s) * P_M(m) corresponds to the
Markov chain S → T → M when T is trivial (Unit). The Ω-on-S-only condition says
the cut depends only on the state, which is the natural scenario when the cut-set
bound is applied to state-based cuts.
-/
lemma condMarkov_of_SM_indep_and_Omega_depends_only_on_S
    (P : FinitePMF (State2 × Unit × Missing2))
    (Ω_vars : (State2 × Unit × Missing2) → CutVar2)
    (h_SM_indep : ∀ (s : State2) (m : Missing2),
      P.pmf (s, (), m) = (∑ m' : Missing2, P.pmf (s, (), m')) * (∑ s' : State2, P.pmf (s', (), m)))
    (h_Omega_S_only : ∀ (s : State2) (m : Missing2), Ω_vars (s, (), m) = Ω_vars (s, (), (0:Missing2)))
    : condMarkov (pmf_from_vars P Ω_vars) := by
  intro s k m ()
  let P4 := pmf_from_vars P Ω_vars
  let f : State2 → CutVar2 := fun s' => Ω_vars (s', (), (0 : Missing2))
  have h_Omega_eq : ∀ (s' : State2) (m' : Missing2), Ω_vars (s', (), m') = f s' := by
    intro s' m'
    calc
      Ω_vars (s', (), m') = Ω_vars (s', (), (0 : Missing2)) := h_Omega_S_only s' m'
      _ = f s' := rfl
  -- Lemma: explicit pmf of P4 at (s, k, m, ())
  have hP4_val : ∀ (x : State2) (z : Missing2), P4.pmf (x, k, z, ()) =
    P.pmf (x, (), z) * (if f x = k then (1 : ℝ) else 0) := by
    intro x z
    dsimp [P4]
    rw [pmf_from_vars_apply]
    rw [h_Omega_eq x z]
    by_cases hx : f x = k
    · simp [hx]
    · simp [hx]
  -- Compute each marginal ingredient in terms of the original P
  have h_margY : marginalYWMass P4 (k, ()) =
    ∑ s' : State2, (∑ m' : Missing2, P.pmf (s', (), m')) * (if f s' = k then (1 : ℝ) else 0) := by
    unfold marginalYWMass
    simp_rw [hP4_val]
    calc
      ∑ x : State2, ∑ z : Missing2, (P.pmf (x, (), z) * (if f x = k then (1 : ℝ) else 0))
          = ∑ x : State2, (∑ z : Missing2, P.pmf (x, (), z)) * (if f x = k then (1 : ℝ) else 0) := by
            refine Finset.sum_congr rfl (fun x _ => ?_)
            rw [← Finset.sum_mul]
      _ = ∑ s' : State2, (∑ m' : Missing2, P.pmf (s', (), m')) * (if f s' = k then (1 : ℝ) else 0) := rfl
  have h_margXY : marginalXYWMass P4 (s, k, ()) =
    (∑ m' : Missing2, P.pmf (s, (), m')) * (if f s = k then (1 : ℝ) else 0) := by
    unfold marginalXYWMass
    simp_rw [hP4_val]
    rw [← Finset.sum_mul]
  have h_margYZ : marginalYZWMass P4 (k, m, ()) =
    ∑ s' : State2, P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0) := by
    unfold marginalYZWMass
    calc
      ∑ s' : State2, P4.pmf (s', k, m, ())
          = ∑ s' : State2, (P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0)) := by
            refine Finset.sum_congr rfl (fun s' _ => ?_)
            rw [hP4_val s' m]
      _ = ∑ s' : State2, P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0) := rfl
  have hP4_single : P4.pmf (s, k, m, ()) = P.pmf (s, (), m) * (if f s = k then (1 : ℝ) else 0) :=
    hP4_val s m
  rw [hP4_single, h_margY, h_margXY, h_margYZ]
  by_cases h : f s = k
  · -- Case: f(s) = k, so the indicator for s reduces to 1
    rw [if_pos h, mul_one, mul_one]
    let PS := fun s' : State2 => ∑ m' : Missing2, P.pmf (s', (), m')
    let PM := fun m' : Missing2 => ∑ s' : State2, P.pmf (s', (), m')
    have h_SM_indep' : ∀ (s' : State2) (m' : Missing2), P.pmf (s', (), m') = PS s' * PM m' := h_SM_indep
    have h_factor : ∑ s' : State2, P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0) =
      PM m * ∑ s' : State2, PS s' * (if f s' = k then (1 : ℝ) else 0) := by
      calc
        ∑ s' : State2, P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0)
            = ∑ s' : State2, (PS s' * PM m) * (if f s' = k then (1 : ℝ) else 0) := by
              refine Finset.sum_congr rfl (fun s' _ => ?_)
              rw [h_SM_indep' s' m]
        _ = ∑ s' : State2, PM m * (PS s' * (if f s' = k then (1 : ℝ) else 0)) := by
          refine Finset.sum_congr rfl (fun s' _ => ?_)
          ring
        _ = PM m * ∑ s' : State2, PS s' * (if f s' = k then (1 : ℝ) else 0) := by
          rw [← Finset.mul_sum]
    calc
      P.pmf (s, (), m) * (∑ s' : State2, PS s' * (if f s' = k then (1 : ℝ) else 0))
          = (PS s * PM m) * (∑ s' : State2, PS s' * (if f s' = k then (1 : ℝ) else 0)) := by
            rw [h_SM_indep' s m]
      _ = PS s * (PM m * ∑ s' : State2, PS s' * (if f s' = k then (1 : ℝ) else 0)) := by ring
      _ = PS s * (∑ s' : State2, P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0)) := by rw [h_factor]
      _ = (∑ m' : Missing2, P.pmf (s, (), m')) * (∑ s' : State2, P.pmf (s', (), m) * (if f s' = k then (1 : ℝ) else 0)) := by
        simp [PS]
  · -- Case: f(s) ≠ k, so the indicator is 0 and both sides vanish
    rw [if_neg h]
    simp

end UnitLemmas

section EndToEnd

theorem linear_chain_cut_set_bound
    (P : FinitePMF (State2 × Unit × Missing2))
    (Ω_vars : (State2 × Unit × Missing2) → CutVar2)
    (h_markov : condMarkov (pmf_from_vars P Ω_vars)) :
    I_S_M_cond_Ttilde P ≤ 1 := by
  let P4 := pmf_from_vars P Ω_vars
  have h_YZ_bound : I_YZ_W P4 ≤ 1 := I_YZ_W_unit_CutVar2_le_one P4
  let cert : KKT_Certificate P4 := KKT_Certificate.of_direct_bound P4 1 h_YZ_bound
  have h_cap : I_YZ_W P4 ≤ 1 := capacity_le_of_kkt P4 cert
  exact abstract_cut_set_bound P Ω_vars 1 h_markov h_cap

/--
End-to-end case-study bound using the DAG automation interface.  The remaining
model-specific premises are: a semantic factorization package for the concrete
four-variable PMF and a d-separation proof for `{0} ⟂ {2} | {1,3}`.
-/
theorem linear_chain_cut_set_bound_from_dag
    (G : DAG)
    (P : FinitePMF (State2 × Unit × Missing2))
    (Ω_vars : (State2 × Unit × Missing2) → CutVar2)
    (h_factor : FactorizesOverDAG G condMarkovNodeCI (pmf_from_vars P Ω_vars))
    (h_dsep : dSeparates G ({0} : Finset ℕ) ({2} : Finset ℕ) ({1, 3} : Finset ℕ)) :
    I_S_M_cond_Ttilde P ≤ 1 := by
  exact linear_chain_cut_set_bound P Ω_vars
    (condMarkov_of_factorizes_dsep_fourVar G (pmf_from_vars P Ω_vars) h_factor h_dsep)

end EndToEnd

end
end FiniteQuerySandbox
