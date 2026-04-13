import FiniteQuerySandbox.Impossibility
import FiniteQuerySandbox.GeometricTools
import Mathlib.Data.Set.Finite.Basic
import Mathlib.Topology.MetricSpace.Basic

namespace FiniteQuerySandbox

variable {E H : Type*} [MetricSpace H]

/-- 
IsGammaSeparatedInjection eta hB gamma 
states that the mapping hB after eta is gamma-separated.
-/
def IsGammaSeparatedInjection (eta : Nat → E) (hB : E → H) (gamma : ℝ) : Prop :=
  ∀ i j : Nat, i ≠ j → dist (hB (eta i)) (hB (eta j)) ≥ gamma

/-- 
Key Packing Lemma: In a gamma-separated set, any point e_star can be 'covered' 
by at most one point from the set if the coverage radius rho is < gamma/2.
-/
lemma packing_lemma {eta : Nat → E} {hB : E → H} {gamma rho : ℝ} 
    (h_rho : rho < gamma / 2)
    (h_sep : IsGammaSeparatedInjection eta hB gamma)
    (n m₁ m₂ : Nat)
    (h1 : dist (hB (eta n)) (hB (eta m₁)) ≤ rho)
    (h2 : dist (hB (eta n)) (hB (eta m₂)) ≤ rho) :
    m₁ = m₂ := by
  by_contra h_neq
  have h_gap : dist (hB (eta m₁)) (hB (eta m₂)) ≥ gamma := h_sep m₁ m₂ h_neq
  have h_tri : dist (hB (eta m₁)) (hB (eta m₂)) ≤ dist (hB (eta m₁)) (hB (eta n)) + dist (hB (eta n)) (hB (eta m₂)) :=
    dist_triangle _ _ _
  rw [dist_comm] at h1
  have h_tri_bound : dist (hB (eta m₁)) (hB (eta m₂)) ≤ rho + rho :=
    le_trans h_tri (add_le_add h1 h2)
  have h_final : gamma ≤ 2 * rho := by
    linarith
  linarith

/--
Theorem: If the encoding space contains an infinite gamma-separated injection (η),
then for any finite support (measured in indices), there remains an index n
that is NOT rho-covered by any element in the support, provided rho < gamma/2.
-/
theorem finite_patch_cannot_cover_separated
    {eta : Nat → E} {hB : E → H} (gamma rho : ℝ) (h_rho : rho < gamma / 2)
    (h_sep : IsGammaSeparatedInjection eta hB gamma)
    (support : List Nat) :
    ∃ n : Nat, ∀ m ∈ support, dist (hB (eta n)) (hB (eta m)) > rho := by
  let n := freshIndex support 0
  refine ⟨n, ?_⟩
  intro m hm
  have hn_not_mem : n ∉ support := by
    simpa [n] using freshIndex_not_mem support 0
  have hne : n ≠ m := by
    intro hnm
    exact hn_not_mem (by
      rw [hnm]
      exact hm)
  have hdist : gamma ≤ dist (hB (eta n)) (hB (eta m)) := h_sep n m hne
  by_cases h_rho_nonneg : 0 ≤ rho
  · have h_rho_lt_gamma : rho < gamma := by
      nlinarith
    exact lt_of_lt_of_le h_rho_lt_gamma hdist
  · have h_rho_neg : rho < 0 := lt_of_not_ge h_rho_nonneg
    exact lt_of_lt_of_le h_rho_neg dist_nonneg

end FiniteQuerySandbox
