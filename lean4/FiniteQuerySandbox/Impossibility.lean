import FiniteQuerySandbox.Tools

namespace FiniteQuerySandbox

/-!
# Finite-Query Impossibility

Preferred reader-facing import:
`FiniteQuerySandbox.FiniteQueryDecisionImpossibility`.

A finite-query certifier cannot be both sound and complete for a global
closedness property when its decision is stable under changes outside the
finite queried support.
-/

def Closed (R : Nat → Bool) : Prop :=
  ∀ i j : Nat, R i = R j

structure FiniteQueryCertifier where
  run : (Nat → Bool) → List Nat × Bool
  stable :
    ∀ {R₁ R₂ : Nat → Bool},
      (∀ n : Nat, n ∈ (run R₁).1 → R₁ n = R₂ n) →
      run R₁ = run R₂

def Sound (C : FiniteQueryCertifier) : Prop :=
  ∀ R : Nat → Bool, (C.run R).2 = true → Closed R

def Complete (C : FiniteQueryCertifier) : Prop :=
  ∀ R : Nat → Bool, Closed R → (C.run R).2 = true

def closedOracle : Nat → Bool := fun _ => false

def openOracle (support : List Nat) : Nat → Bool :=
  fun n => if n = freshIndex support 0 then true else false

theorem closedOracle_closed : Closed closedOracle := by
  intro i j
  rfl

theorem openOracle_not_closed (support : List Nat) : ¬ Closed (openOracle support) := by
  intro hClosed
  have hEq : openOracle support (freshIndex support 0) = openOracle support (freshIndex support 0 + 1) :=
    hClosed (freshIndex support 0) (freshIndex support 0 + 1)
  have hLeft : openOracle support (freshIndex support 0) = true := by
    unfold openOracle
    simp
  have hRight : openOracle support (freshIndex support 0 + 1) = false := by
    unfold openOracle
    apply if_neg
    intro hEqSucc
    have hSucc : (freshIndex support 0).succ = freshIndex support 0 := by
      simpa [Nat.succ_eq_add_one] using hEqSucc.symm
    exact Nat.succ_ne_self (freshIndex support 0) hSucc
  have : true = false := by
    calc
      true = openOracle support (freshIndex support 0) := hLeft.symm
      _ = openOracle support (freshIndex support 0 + 1) := hEq
      _ = false := hRight
  exact Bool.false_ne_true this.symm

theorem openOracle_agrees_on_support
    (support : List Nat) :
    ∀ n : Nat, n ∈ support → closedOracle n = openOracle support n := by
  intro n hMem
  unfold closedOracle openOracle
  symm
  apply if_neg
  intro hEq
  exact freshIndex_not_mem support 0 (hEq ▸ hMem)

theorem finite_query_impossibility (C : FiniteQueryCertifier) :
    ¬ (Sound C ∧ Complete C) := by
  intro h
  rcases h with ⟨hSound, hComplete⟩
  let support := (C.run closedOracle).1
  have hAcceptClosed : (C.run closedOracle).2 = true :=
    hComplete closedOracle closedOracle_closed
  have hRunEq : C.run closedOracle = C.run (openOracle support) :=
    C.stable (R₁ := closedOracle) (R₂ := openOracle support) (openOracle_agrees_on_support support)
  have hAcceptOpen : (C.run (openOracle support)).2 = true := by
    rw [← hRunEq]
    exact hAcceptClosed
  have hClosedOpen : Closed (openOracle support) :=
    hSound (openOracle support) hAcceptOpen
  exact openOracle_not_closed support hClosedOpen

def rejectAllCertifier : FiniteQueryCertifier where
  run _ := ([], false)
  stable := by
    intro R₁ R₂ h
    rfl

end FiniteQuerySandbox
