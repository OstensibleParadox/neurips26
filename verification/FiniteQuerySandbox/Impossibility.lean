import FiniteQuerySandbox.Tools

namespace FiniteQuerySandbox

def Injective {α β : Type} (f : α → β) : Prop :=
  ∀ ⦃a b : α⦄, f a = f b → a = b

def supportBound : List Nat → Nat
  | [] => 0
  | x :: xs => Nat.max x (supportBound xs)

theorem mem_le_supportBound {n : Nat} :
    ∀ {support : List Nat}, n ∈ support → n ≤ supportBound support
  | [], h => nomatch h
  | x :: xs, h => by
      simp only [supportBound]
      simp only [List.mem_cons] at h
      cases h with
      | inl hEq =>
          rw [hEq]
          exact Nat.le_max_left x (supportBound xs)
      | inr hTail =>
          exact Nat.le_trans (mem_le_supportBound hTail) (Nat.le_max_right x (supportBound xs))

def freshIndex (support : List Nat) (k : Nat) : Nat :=
  k + supportBound support + 1

theorem supportBound_lt_freshIndex (support : List Nat) (k : Nat) :
    supportBound support < freshIndex support k := by
  unfold freshIndex
  have hle : supportBound support ≤ k + supportBound support := by
    exact Nat.le_add_left (supportBound support) k
  simpa [Nat.succ_eq_add_one, Nat.add_assoc] using Nat.lt_succ_of_le hle

theorem freshIndex_not_mem (support : List Nat) (k : Nat) :
    freshIndex support k ∉ support := by
  intro hMem
  have hLe : freshIndex support k ≤ supportBound support :=
    mem_le_supportBound hMem
  have hLt : supportBound support < freshIndex support k :=
    supportBound_lt_freshIndex support k
  exact Nat.not_lt_of_ge hLe hLt

theorem finite_patch_cannot_complete (support : List Nat) :
    ∃ n : Nat, n ∉ support := by
  exact ⟨freshIndex support 0, freshIndex_not_mem support 0⟩

theorem infinite_residual_indices (support : List Nat) :
    ∀ k : Nat, ∃ n : Nat, k ≤ n ∧ n ∉ support := by
  intro k
  refine ⟨freshIndex support k, ?_, freshIndex_not_mem support k⟩
  unfold freshIndex
  exact Nat.le_add_right k (supportBound support + 1)

theorem encoded_fresh_not_mem
    {α : Type} {encode : Nat → α}
    (hInj : Injective encode) (support : List Nat) (k : Nat) :
    encode (freshIndex support k) ∉ support.map encode := by
  intro hMem
  rcases (List.mem_map.mp hMem) with ⟨m, hMemSupport, hEq⟩
  have hFreshEq : freshIndex support k = m := hInj hEq.symm
  exact freshIndex_not_mem support k (hFreshEq ▸ hMemSupport)

theorem encoded_infinite_residual
    {α : Type} {encode : Nat → α}
    (hInj : Injective encode) (support : List Nat) :
    ∀ k : Nat, ∃ n : Nat, k ≤ n ∧ encode n ∉ support.map encode := by
  intro k
  refine ⟨freshIndex support k, ?_, encoded_fresh_not_mem hInj support k⟩
  unfold freshIndex
  exact Nat.le_add_right k (supportBound support + 1)

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

example : freshIndex [1, 4, 7] 0 ∉ ([1, 4, 7] : List Nat) :=
  freshIndex_not_mem [1, 4, 7] 0

example : ∃ n : Nat, 10 ≤ n ∧ n ∉ ([1, 4, 7] : List Nat) :=
  infinite_residual_indices [1, 4, 7] 10

def rejectAllCertifier : FiniteQueryCertifier where
  run _ := ([], false)
  stable := by
    intro R₁ R₂ h
    rfl

example : ¬ (Sound rejectAllCertifier ∧ Complete rejectAllCertifier) :=
  finite_query_impossibility rejectAllCertifier

end FiniteQuerySandbox
