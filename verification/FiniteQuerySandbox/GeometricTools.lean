import Mathlib.Data.Real.Basic
import Mathlib.MeasureTheory.Measure.ProbabilityMeasure
import Mathlib.Topology.MetricSpace.Basic

open MeasureTheory
open scoped ENNReal

namespace FiniteQuerySandbox

variable {E H : Type*}

/-- The representation distance is normalized to the unit interval. -/
def NormalizedReprDist (d_repr : H → H → ℝ) : Prop :=
  ∀ h1 h2, 0 ≤ d_repr h1 h2 ∧ d_repr h1 h2 ≤ 1

/-- Representation-induced similarity: `1 - d_repr (hB e1) (hB e2)`. -/
def ReprSim (hB : E → H) (d_repr : H → H → ℝ) (e1 e2 : E) : ℝ :=
  1 - d_repr (hB e1) (hB e2)

/-- A `ρ`-cover of `S` by seen points in the representation geometry. -/
def IsRhoCover (hB : E → H) (d_repr : H → H → ℝ) (D S : Set E) (ρ : ℝ) : Prop :=
  ∀ e_star ∈ S, ∃ e_0 ∈ D, d_repr (hB e_star) (hB e_0) ≤ ρ

/-- Reward smoothness relative to the representation distance. -/
def LipschitzOnRepresentation
    (R : E → ℝ) (hB : E → H) (d_repr : H → H → ℝ) (L : ℝ) : Prop :=
  ∀ e1 e2, |R e1 - R e2| ≤ L * d_repr (hB e1) (hB e2)

/-- Format-Channel Gap using the representation-induced similarity. -/
def FCG (R : E → ℝ) (hB : E → H) (d_repr : H → H → ℝ) (e1 e2 : E) : ℝ :=
  |R e1 - R e2| * ReprSim hB d_repr e1 e2

/-- The set of points admitting a seen witness with `FCG ≤ L * ρ`. -/
def GoodFCGSet
    (R : E → ℝ) (hB : E → H) (d_repr : H → H → ℝ)
    (Seen : Set E) (L ρ : ℝ) : Set E :=
  {e | ∃ e0 ∈ Seen, FCG R hB d_repr e e0 ≤ L * ρ}

section MeasureRegions

variable [MeasurableSpace E]

/-- A measurable region whose complement has measure at most `ε`. -/
def HighProbRegion (μ : Measure E) (ε : ℝ≥0∞) (S : Set E) : Prop :=
  MeasurableSet S ∧ μ Sᶜ ≤ ε

end MeasureRegions

lemma reprSim_nonneg
    {hB : E → H} {d_repr : H → H → ℝ}
    (hd_repr : NormalizedReprDist d_repr) (e1 e2 : E) :
    0 ≤ ReprSim hB d_repr e1 e2 := by
  unfold ReprSim
  exact sub_nonneg.mpr (hd_repr (hB e1) (hB e2)).2

lemma reprSim_le_one
    {hB : E → H} {d_repr : H → H → ℝ}
    (hd_repr : NormalizedReprDist d_repr) (e1 e2 : E) :
    ReprSim hB d_repr e1 e2 ≤ 1 := by
  unfold ReprSim
  exact sub_le_self _ (hd_repr (hB e1) (hB e2)).1

lemma reprSim_mem_unitInterval
    {hB : E → H} {d_repr : H → H → ℝ}
    (hd_repr : NormalizedReprDist d_repr) (e1 e2 : E) :
    0 ≤ ReprSim hB d_repr e1 e2 ∧ ReprSim hB d_repr e1 e2 ≤ 1 := by
  exact ⟨reprSim_nonneg hd_repr e1 e2, reprSim_le_one hd_repr e1 e2⟩

end FiniteQuerySandbox
