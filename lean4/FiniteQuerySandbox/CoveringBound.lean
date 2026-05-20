import FiniteQuerySandbox.GeometricTools
import Mathlib.Data.Real.Basic
import Mathlib.MeasureTheory.Measure.ProbabilityMeasure

open MeasureTheory
open scoped ENNReal

namespace FiniteQuerySandbox

variable {E H : Type*}

theorem fcg_covering_bound
    {R : E → ℝ} {hB : E → H} {d_repr : H → H → ℝ}
    {Seen S : Set E} {L ρ : ℝ}
    (hcover : IsRhoCover hB d_repr Seen S ρ)
    (hLip : LipschitzOnRepresentation R hB d_repr L)
    (hd_repr : NormalizedReprDist d_repr)
    (hL_nonneg : 0 ≤ L)
    {e : E} (he : e ∈ S) :
    ∃ e0 ∈ Seen, FCG R hB d_repr e e0 ≤ L * ρ := by
  rcases hcover e he with ⟨e0, he0, hd⟩
  use e0, he0

  unfold FCG

  have hreward : |R e - R e0| ≤ L * d_repr (hB e) (hB e0) := hLip e e0
  have hd_bound : L * d_repr (hB e) (hB e0) ≤ L * ρ :=
    mul_le_mul_of_nonneg_left hd hL_nonneg
  have hreward_rho : |R e - R e0| ≤ L * ρ := le_trans hreward hd_bound

  have hsim_bound : ReprSim hB d_repr e e0 ≤ 1 := reprSim_le_one hd_repr e e0
  have abs_nonneg : 0 ≤ |R e - R e0| := abs_nonneg _
  have h_fcg_le :
      |R e - R e0| * ReprSim hB d_repr e e0 ≤ |R e - R e0| * 1 :=
    mul_le_mul_of_nonneg_left hsim_bound abs_nonneg
  rw [mul_one] at h_fcg_le

  exact le_trans h_fcg_le hreward_rho

theorem subset_goodFCGSet_of_cover
    {R : E → ℝ} {hB : E → H} {d_repr : H → H → ℝ}
    {Seen S : Set E} {L ρ : ℝ}
    (hcover : IsRhoCover hB d_repr Seen S ρ)
    (hLip : LipschitzOnRepresentation R hB d_repr L)
    (hd_repr : NormalizedReprDist d_repr)
    (hL_nonneg : 0 ≤ L) :
    S ⊆ GoodFCGSet R hB d_repr Seen L ρ := by
  intro e he
  exact fcg_covering_bound hcover hLip hd_repr hL_nonneg he

section MeasureBounds

variable [MeasurableSpace E]

/-- A measurable region whose complement has measure at most `ε`. -/
def HighProbRegion (μ : Measure E) (ε : ℝ≥0∞) (S : Set E) : Prop :=
  MeasurableSet S ∧ μ Sᶜ ≤ ε

theorem goodFCGSet_compl_mass_le
    {R : E → ℝ} {hB : E → H} {d_repr : H → H → ℝ}
    {Seen S : Set E} {L ρ : ℝ}
    {μ : Measure E} {ε : ℝ≥0∞}
    (hcover : IsRhoCover hB d_repr Seen S ρ)
    (hLip : LipschitzOnRepresentation R hB d_repr L)
    (hd_repr : NormalizedReprDist d_repr)
    (hL_nonneg : 0 ≤ L)
    (hS_mass : HighProbRegion μ ε S) :
    μ (GoodFCGSet R hB d_repr Seen L ρ)ᶜ ≤ ε := by
  have hsubset : S ⊆ GoodFCGSet R hB d_repr Seen L ρ :=
    subset_goodFCGSet_of_cover hcover hLip hd_repr hL_nonneg
  have hcompl_subset : (GoodFCGSet R hB d_repr Seen L ρ)ᶜ ⊆ Sᶜ :=
    Set.compl_subset_compl.mpr hsubset
  exact le_trans (measure_mono hcompl_subset) hS_mass.2

theorem goodFCGSet_highProb
    {R : E → ℝ} {hB : E → H} {d_repr : H → H → ℝ}
    {Seen S : Set E} {L ρ : ℝ}
    {μ : Measure E} {ε : ℝ≥0∞}
    (hcover : IsRhoCover hB d_repr Seen S ρ)
    (hLip : LipschitzOnRepresentation R hB d_repr L)
    (hd_repr : NormalizedReprDist d_repr)
    (hL_nonneg : 0 ≤ L)
    (hGood_meas : MeasurableSet (GoodFCGSet R hB d_repr Seen L ρ))
    (hS_mass : HighProbRegion μ ε S) :
    HighProbRegion μ ε (GoodFCGSet R hB d_repr Seen L ρ) := by
  exact ⟨hGood_meas, goodFCGSet_compl_mass_le hcover hLip hd_repr hL_nonneg hS_mass⟩

theorem goodFCGSet_mass_ge_one_sub_eps
    {R : E → ℝ} {hB : E → H} {d_repr : H → H → ℝ}
    {Seen : Set E} {L ρ : ℝ}
    {μ : Measure E} [IsProbabilityMeasure μ] {ε : ℝ≥0∞}
    (hGood_highProb : HighProbRegion μ ε (GoodFCGSet R hB d_repr Seen L ρ)) :
    1 - ε ≤ μ (GoodFCGSet R hB d_repr Seen L ρ) := by
  refine tsub_le_iff_right.mpr ?_
  calc
    (1 : ℝ≥0∞) = μ (GoodFCGSet R hB d_repr Seen L ρ) + μ (GoodFCGSet R hB d_repr Seen L ρ)ᶜ := by
      simpa using (prob_add_prob_compl (μ := μ) hGood_highProb.1).symm
    _ ≤ μ (GoodFCGSet R hB d_repr Seen L ρ) + ε := by
      simpa [add_comm, add_left_comm, add_assoc] using
        add_le_add_right hGood_highProb.2 (μ (GoodFCGSet R hB d_repr Seen L ρ))

theorem goodFCGSet_mass_ge_one_sub_eps_of_cover
    {R : E → ℝ} {hB : E → H} {d_repr : H → H → ℝ}
    {Seen S : Set E} {L ρ : ℝ}
    {μ : Measure E} [IsProbabilityMeasure μ] {ε : ℝ≥0∞}
    (hcover : IsRhoCover hB d_repr Seen S ρ)
    (hLip : LipschitzOnRepresentation R hB d_repr L)
    (hd_repr : NormalizedReprDist d_repr)
    (hL_nonneg : 0 ≤ L)
    (hGood_meas : MeasurableSet (GoodFCGSet R hB d_repr Seen L ρ))
    (hS_mass : HighProbRegion μ ε S) :
    1 - ε ≤ μ (GoodFCGSet R hB d_repr Seen L ρ) := by
  exact goodFCGSet_mass_ge_one_sub_eps
    (goodFCGSet_highProb hcover hLip hd_repr hL_nonneg hGood_meas hS_mass)

end MeasureBounds

end FiniteQuerySandbox
