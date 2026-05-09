import Init.Data.List.Basic
import Init.Data.List.Lemmas

namespace FiniteQuerySandbox

/-!
# Finite Support Utilities

Small list lemmas used by the finite-query impossibility and geometric
non-covering arguments.
-/

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
    (hInj : Function.Injective encode) (support : List Nat) (k : Nat) :
    encode (freshIndex support k) ∉ support.map encode := by
  intro hMem
  rcases (List.mem_map.mp hMem) with ⟨m, hMemSupport, hEq⟩
  have hFreshEq : freshIndex support k = m := hInj hEq.symm
  exact freshIndex_not_mem support k (hFreshEq ▸ hMemSupport)

theorem encoded_infinite_residual
    {α : Type} {encode : Nat → α}
    (hInj : Function.Injective encode) (support : List Nat) :
    ∀ k : Nat, ∃ n : Nat, k ≤ n ∧ encode n ∉ support.map encode := by
  intro k
  refine ⟨freshIndex support k, ?_, encoded_fresh_not_mem hInj support k⟩
  unfold freshIndex
  exact Nat.le_add_right k (supportBound support + 1)

end FiniteQuerySandbox
