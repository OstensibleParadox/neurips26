import Init.Data.List.Basic
import Init.Data.List.Lemmas
import Init.Data.List.Pairwise
import Init.Data.List.Sublist
import Init.Data.List.Range

namespace FiniteQuerySandbox

-- Smoke tests for the list toolkit needed by the finite-query impossibility sandbox.

example : (List.range 5).length = 5 := by
  simp

example : 3 ∈ List.range 5 := by
  simp [List.mem_range]

example : (¬ 5 ∈ List.range 5) := by
  simp [List.mem_range]

example : ([0, 1, 2] : List Nat).Nodup := by
  decide

example : List.Pairwise (· < ·) ([0, 1, 2] : List Nat) := by
  decide

example {α : Type} {xs : List α} {n : Nat} (h : n < xs.length) : xs[n] ∈ xs :=
  List.getElem_mem h

example {α β : Type} (f : α → β) (xs : List α) :
    (xs.map f).length = xs.length :=
  List.length_map f

example {α : Type} {xs ys : List α} (h : List.Sublist xs ys) : xs.length ≤ ys.length :=
  List.Sublist.length_le h

end FiniteQuerySandbox
