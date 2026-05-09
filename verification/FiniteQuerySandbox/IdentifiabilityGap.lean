import FiniteQuerySandbox.InfoTheory

namespace FiniteQuerySandbox

open Finset
open scoped BigOperators Real

/-!
# Theorem 1: Output-Trace Identifiability Gap

Axiom-free construction of two behaviorally-equivalent but audit-inequivalent
finite PMFs P₀, P₁ on S × T × A.
-/

set_option maxHeartbeats 400000
noncomputable section

variable {S T A : Type} [Fintype S] [Fintype T] [Fintype A]
  [DecidableEq S] [DecidableEq T] [DecidableEq A]

/-! ### Helper lemmas -/

lemma negMulLog2_zero : negMulLog2 (0 : ℝ) = 0 := by
  simp [negMulLog2]

lemma sum_ite_dirac (x : ℝ) (s0 : S) : ∑ s : S, (if s = s0 then x else 0) = x := by
  simp

/-- `∑ₛ negMulLog₂ (I[s=s₀]·x) = negMulLog₂ x` — only the s=s₀ term contributes. -/
lemma entropy_sum_dirac (x : ℝ) (s0 : S) :
    ∑ s : S, negMulLog2 (if s = s0 then x else 0) = negMulLog2 x := by
  calc
    ∑ s : S, negMulLog2 (if s = s0 then x else 0)
        = ∑ s : S, (if s = s0 then negMulLog2 x else negMulLog2 (0 : ℝ)) := by
          simp [negMulLog2]
    _ = ∑ s : S, (if s = s0 then negMulLog2 x else 0) := by simp [negMulLog2_zero]
    _ = negMulLog2 x := by simp

/-- `∑ₛ negMulLog₂ (I[s=φ a]·x) = negMulLog₂ x`. Exactly one s matches φ a. -/
lemma entropy_sum_inj (x : ℝ) (φ : A → S) (a : A) :
    ∑ s : S, negMulLog2 (if s = φ a then x else 0) = negMulLog2 x := by
  calc
    ∑ s : S, negMulLog2 (if s = φ a then x else 0)
        = ∑ s : S, (if s = φ a then negMulLog2 x else negMulLog2 (0 : ℝ)) := by
          simp [negMulLog2]
    _ = ∑ s : S, (if s = φ a then negMulLog2 x else 0) := by simp [negMulLog2_zero]
    _ = negMulLog2 x := by simp

/--
Key lemma: for an injective φ, summing negMulLog₂ over all s of the φ-indexed
inner sum equals summing negMulLog₂ of the original Q terms over all a.
-/
lemma entropy_sum_image (φ : A → S) (hφ_inj : Function.Injective φ)
    (Qpmf : T × A → ℝ) (t : T) :
    ∑ s : S, negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0))
    = ∑ a : A, negMulLog2 (Qpmf (t, a)) := by
  -- restrict to image(φ); outside the image the inner sum is 0, negMulLog₂ 0 = 0
  have h_support : (Finset.univ : Finset S) =
      Finset.image φ Finset.univ ∪ ((Finset.univ : Finset S) \ Finset.image φ Finset.univ) := by
    simp
  have h_disjoint : Disjoint (Finset.image φ Finset.univ)
      ((Finset.univ : Finset S) \ Finset.image φ Finset.univ) := by
    simp
  calc
    ∑ s : S, negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0))
        = ∑ s ∈ (Finset.univ : Finset S),
            negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0)) := by simp
    _ = (∑ s ∈ Finset.image φ Finset.univ,
            negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0))) +
        (∑ s ∈ (Finset.univ : Finset S) \ Finset.image φ Finset.univ,
            negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0))) := by
      rw [Finset.sum_union h_disjoint]
    _ = (∑ s ∈ Finset.image φ Finset.univ,
            negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0))) + 0 := by
      -- for s ∉ image(φ), s ≠ φ a for all a, so inner sum = 0, negMulLog₂ 0 = 0
      congr 1
      refine Finset.sum_eq_zero (fun s hs => ?_)
      have hs' : s ∉ Finset.image φ Finset.univ := Finset.mem_sdiff.mp hs |>.2
      have h_all_neq : ∀ a : A, s ≠ φ a := by
        intro a h_eq
        apply hs'
        exact Finset.mem_image.mpr ⟨a, Finset.mem_univ _, h_eq⟩
      simp [h_all_neq, negMulLog2_zero]
    _ = ∑ s ∈ Finset.image φ Finset.univ,
            negMulLog2 (∑ a : A, (if s = φ a then Qpmf (t, a) else 0)) := by simp
    _ = ∑ a : A,
            negMulLog2 (∑ a' : A, (if φ a = φ a' then Qpmf (t, a') else 0)) := by
      rw [Finset.sum_image (fun x _ y _ h => hφ_inj h)]
    _ = ∑ a : A, negMulLog2 (Qpmf (t, a)) := by
      refine Finset.sum_congr rfl (fun a ha => ?_)
      have h_inner : (∑ a' : A, (if φ a = φ a' then Qpmf (t, a') else 0)) = Qpmf (t, a) := by
        simp [hφ_inj.eq_iff]
      simp [h_inner]

/-! ### Theorem 1 -/

theorem identifiability_gap_extremes
    (Q : FinitePMF (T × A))
    (hT : ∀ t, marginalLeftMass Q t > 0)
    (s0 : S)
    (h_card : Fintype.card A ≤ Fintype.card S) :
    ∃ (P0 P1 : FinitePMF (S × T × A)),
      (∀ t a, marginalTAofSTA P0 (t, a) = Q.pmf (t, a)) ∧
      (∀ t a, marginalTAofSTA P1 (t, a) = Q.pmf (t, a)) ∧
      I_SA_cond_T P0 = 0 ∧
      I_SA_cond_T P1 = H_A_cond_T Q :=
by
  -- Construct injection φ : A → S
  let eA : A ≃ Fin (Fintype.card A) := Fintype.equivFin A
  let eS : S ≃ Fin (Fintype.card S) := Fintype.equivFin S
  let φ : A → S := eS.symm ∘ (Fin.castLE h_card) ∘ (eA : A → Fin (Fintype.card A))
  have hφ_inj : Function.Injective φ := by
    -- all three components are injective
    have h1 : Function.Injective (eA : A → Fin (Fintype.card A)) := eA.injective
    have h2 : Function.Injective (Fin.castLE h_card) :=
      fun a b h => Fin.ext (by
        have := congrArg Fin.val h; simpa using this)
    have h3 : Function.Injective eS.symm := eS.symm.injective
    exact h3.comp (h2.comp h1)

  -- ============================================================
  -- P₀: Dirac state (s = s₀ constant)
  -- ============================================================
  let P0 : FinitePMF (S × T × A) := {
    pmf := fun x : S × T × A =>
      if x.1 = s0 then Q.pmf (x.2.1, x.2.2) else 0
    pmf_nonneg := by
      intro x; dsimp; split
      · exact Q.pmf_nonneg _
      · exact le_refl 0
    sum_one := by
      simp [Finset.sum_add_distrib, Finset.sum_ite_eq, Q.sum_one]
  }

  have h_marg0 : ∀ t a, marginalTAofSTA P0 (t, a) = Q.pmf (t, a) := by
    intro t a; simp [marginalTAofSTA, P0]

  have h_I0 : I_SA_cond_T P0 = 0 := by
    dsimp [I_SA_cond_T]
    set qT := fun (t : T) => ∑ a : A, Q.pmf (t, a) with hqT

    -- H_ST(s,t) = I[s=s₀]·qT(t)  →  entropy = H(qT)
    have h_H_ST : entropyOf (fun (st : S × T) => ∑ a : A, P0.pmf (st.1, st.2, a))
               = entropyOf qT := by
      have h_eq : (fun (st : S × T) => ∑ a : A, P0.pmf (st.1, st.2, a))
                = (fun (st : S × T) => if st.1 = s0 then qT st.2 else 0) := by
        ext ⟨s, t⟩; simp [P0, hqT]
      rw [h_eq]
      calc
        entropyOf (fun (st : S × T) => if st.1 = s0 then qT st.2 else 0)
            = ∑ s : S, ∑ t : T, negMulLog2 (if s = s0 then qT t else 0) := by
              simp [entropyOf, Finset.sum_product]
        _ = ∑ t : T, negMulLog2 (qT t) := by simp [Finset.sum_comm, entropy_sum_dirac]
        _ = entropyOf qT := rfl

    -- H_AT(t,a) = Q(t,a)  (marginal over Dirac S)
    have h_H_AT : entropyOf (fun (ta : T × A) => ∑ s : S, P0.pmf (s, ta.1, ta.2))
               = entropyOf Q.pmf := by
      have h_eq : (fun (ta : T × A) => ∑ s : S, P0.pmf (s, ta.1, ta.2)) = Q.pmf := by
        ext ⟨t, a⟩; simp [P0]
      rw [h_eq]

    -- H_T(t) = qT(t)
    have h_H_T : entropyOf (fun (t : T) => ∑ s : S, ∑ a : A, P0.pmf (s, t, a))
              = entropyOf qT := by
      have h_eq : (fun (t : T) => ∑ s : S, ∑ a : A, P0.pmf (s, t, a)) = qT := by
        ext t; simp [P0, hqT]
      rw [h_eq]

    -- H_STA = H(Q)  (Dirac collapses out)
    have h_H_STA : entropyOf P0.pmf = entropyOf Q.pmf := by
      calc
        entropyOf P0.pmf = ∑ s : S, ∑ t : T, ∑ a : A, negMulLog2 (P0.pmf (s, t, a)) := by
          simp [entropyOf, Finset.sum_product]
        _ = ∑ s : S, ∑ t : T, ∑ a : A, negMulLog2 (if s = s0 then Q.pmf (t, a) else 0) := rfl
        _ = ∑ t : T, ∑ a : A, negMulLog2 (Q.pmf (t, a)) := by
          simp [Finset.sum_comm, entropy_sum_dirac]
        _ = entropyOf Q.pmf := by simp [entropyOf, Finset.sum_product]

    -- I = H_ST + H_AT - H_T - H_STA = H(qT) + H(Q) - H(qT) - H(Q) = 0
    calc
      (entropyOf (fun (st : S × T) => ∑ a : A, P0.pmf (st.1, st.2, a)) +
       entropyOf (fun (ta : T × A) => ∑ s : S, P0.pmf (s, ta.1, ta.2)) -
       entropyOf (fun (t : T) => ∑ s : S, ∑ a : A, P0.pmf (s, t, a)) -
       entropyOf P0.pmf)
          = (entropyOf qT + entropyOf Q.pmf - entropyOf qT - entropyOf Q.pmf) := by
            rw [h_H_ST, h_H_AT, h_H_T, h_H_STA]
      _ = 0 := by ring

  -- ============================================================
  -- P₁: State copies action (s = φ(a))
  -- ============================================================
  let P1 : FinitePMF (S × T × A) := {
    pmf := fun x : S × T × A =>
      if x.1 = φ x.2.2 then Q.pmf (x.2.1, x.2.2) else 0
    pmf_nonneg := by
      intro x; dsimp; split
      · exact Q.pmf_nonneg _
      · exact le_refl 0
    sum_one := by
      calc
        ∑ x : S × T × A, (if x.1 = φ x.2.2 then Q.pmf (x.2.1, x.2.2) else 0)
            = ∑ s : S, ∑ t : T, ∑ a : A, (if s = φ a then Q.pmf (t, a) else 0) := by
              simp [Finset.sum_product]
        _ = ∑ t : T, ∑ a : A, (∑ s : S, if s = φ a then Q.pmf (t, a) else 0) := by
              simp [Finset.sum_comm]
        _ = ∑ t : T, ∑ a : A, Q.pmf (t, a) := by simp
        _ = 1 := by simp [Q.sum_one, Finset.sum_product]
  }

  have h_marg1 : ∀ t a, marginalTAofSTA P1 (t, a) = Q.pmf (t, a) := by
    intro t a; simp [marginalTAofSTA, P1]

  -- I(S;A|T) = H(A|T) because S = φ(A) (injective)
  have h_I1 : I_SA_cond_T P1 = H_A_cond_T Q := by
    dsimp [I_SA_cond_T, H_A_cond_T]
    set qT := fun (t : T) => ∑ a : A, Q.pmf (t, a) with hqT

    -- H_AT(t,a) = Q(t,a)  (marginal projection)
    have h_H_AT : entropyOf (fun (ta : T × A) => ∑ s : S, P1.pmf (s, ta.1, ta.2))
               = entropyOf Q.pmf := by
      have h_eq : (fun (ta : T × A) => ∑ s : S, P1.pmf (s, ta.1, ta.2)) = Q.pmf := by
        ext ⟨t, a⟩; simp [P1]
      rw [h_eq]

    -- H_T(t) = qT(t)  (marginal projection)
    have h_H_T : entropyOf (fun (t : T) => ∑ s : S, ∑ a : A, P1.pmf (s, t, a))
              = entropyOf qT := by
      have h_eq : (fun (t : T) => ∑ s : S, ∑ a : A, P1.pmf (s, t, a)) = qT := by
        ext t; simp [P1, hqT]
      rw [h_eq]

    -- H_STA = H(Q)  (each (t,a) maps to exactly one (φ a, t, a))
    have h_H_STA : entropyOf P1.pmf = entropyOf Q.pmf := by
      calc
        entropyOf P1.pmf = ∑ s : S, ∑ t : T, ∑ a : A,
            negMulLog2 (if s = φ a then Q.pmf (t, a) else 0) := by
          simp [entropyOf, P1, Finset.sum_product]
        _ = ∑ t : T, ∑ a : A, negMulLog2 (Q.pmf (t, a)) := by
          simp [Finset.sum_comm, entropy_sum_inj]
        _ = entropyOf Q.pmf := by simp [entropyOf, Finset.sum_product]

    -- H_ST = H(Q) — uses injectivity via entropy_sum_image
    have h_H_ST : entropyOf (fun (st : S × T) => ∑ a : A, P1.pmf (st.1, st.2, a))
               = entropyOf Q.pmf := by
      calc
        entropyOf (fun (st : S × T) => ∑ a : A, P1.pmf (st.1, st.2, a))
            = ∑ s : S, ∑ t : T, negMulLog2 (∑ a : A, (if s = φ a then Q.pmf (t, a) else 0)) := by
              simp [entropyOf, P1, Finset.sum_product]
        _ = ∑ t : T, ∑ s : S, negMulLog2 (∑ a : A, (if s = φ a then Q.pmf (t, a) else 0)) := by
              simp [Finset.sum_comm]
        _ = ∑ t : T, ∑ a : A, negMulLog2 (Q.pmf (t, a)) := by
              simp [entropy_sum_image φ hφ_inj Q.pmf]
        _ = entropyOf Q.pmf := by simp [entropyOf, Finset.sum_product]

    -- I = H_ST + H_AT - H_T - H_STA
    --   = H(Q) + H(Q) - H(qT) - H(Q)
    --   = H(Q) - H(qT) = H_A_cond_T Q
    calc
      (entropyOf (fun (st : S × T) => ∑ a : A, P1.pmf (st.1, st.2, a)) +
       entropyOf (fun (ta : T × A) => ∑ s : S, P1.pmf (s, ta.1, ta.2)) -
       entropyOf (fun (t : T) => ∑ s : S, ∑ a : A, P1.pmf (s, t, a)) -
       entropyOf P1.pmf)
          = (entropyOf Q.pmf + entropyOf Q.pmf - entropyOf qT - entropyOf Q.pmf) := by
            rw [h_H_ST, h_H_AT, h_H_T, h_H_STA]
      _ = entropyOf Q.pmf - entropyOf qT := by ring
      _ = (entropyOf Q.pmf - entropyOf (marginalLeftMass Q)) := by
            have h_qT_left : qT = marginalLeftMass Q := by
              ext t; simp [qT, hqT, marginalLeftMass, Finset.sum_comm]
            rw [h_qT_left]
      _ = H_A_cond_T Q := rfl

  exact ⟨P0, P1, h_marg0, h_marg1, h_I0, h_I1⟩

end

end FiniteQuerySandbox
