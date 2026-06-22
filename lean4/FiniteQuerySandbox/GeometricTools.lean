import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Data.Real.Basic

namespace FiniteQuerySandbox

variable {E H : Type*}

/-- The representation distance is normalized to the unit interval. -/
def NormalizedReprDist (d_repr : H → H → ℝ) : Prop :=
  ∀ h1 h2, 0 ≤ d_repr h1 h2 ∧ d_repr h1 h2 ≤ 1

/-- Explicit structure for representation distances. -/
structure ReprDist (H : Type*) where
  dist : H → H → ℝ
  dist_self : ∀ x, dist x x = 0
  dist_nonneg : ∀ x y, 0 ≤ dist x y
  dist_le_one : ∀ x y, dist x y ≤ 1

instance (D : ReprDist H) : NormalizedReprDist D.dist :=
  fun x y => ⟨D.dist_nonneg x y, D.dist_le_one x y⟩

/-- Representation-induced similarity: `1 - d_repr (hB e1) (hB e2)`. -/
def ReprSim (hB : E → H) (d_repr : H → H → ℝ) (e1 e2 : E) : ℝ :=
  1 - d_repr (hB e1) (hB e2)

/-- A `ρ`-cover of `S` by seen points in the representation geometry. -/
def IsRhoCover (hB : E → H) (d_repr : H → H → ℝ) (D S : Set E) (ρ : ℝ) : Prop :=
  ∀ e_star ∈ S, ∃ e_0 ∈ D, d_repr (hB e_star) (hB e_0) ≤ ρ

/-- An internal `ρ`-cover of `S` by finite centers `C ⊆ S` in representation space `H`. -/
def IsRhoCoverFinset (d : H → H → ℝ) (C S : Finset H) (ρ : ℝ) : Prop :=
  ∀ x ∈ S, ∃ y ∈ C, d x y ≤ ρ

/-- A `ρ`-separated set `C` in the representation space `H`. -/
def IsRhoSeparated (d : H → H → ℝ) (C : Finset H) (ρ : ℝ) : Prop :=
  ∀ x ∈ C, ∀ y ∈ C, x ≠ y → ρ < d x y

/-- Reward smoothness relative to the representation distance. -/
def LipschitzOnRepresentation
    (R : E → ℝ) (hB : E → H) (d_repr : H → H → ℝ) (L : ℝ) : Prop :=
  ∀ e1 e2, |R e1 - R e2| ≤ L * d_repr (hB e1) (hB e2)

/-- Format-Channel Gap using the representation-induced similarity. -/
def FCG (R : E → ℝ) (hB : E → H) (d_repr : H → H → ℝ) (e1 e2 : E) : ℝ :=
  |R e1 - R e2| * ReprSim hB d_repr e1 e2

theorem exists_cover_card [DecidableEq H] (d : H → H → ℝ) (hd_self : ∀ x, d x x = 0)
    (S : Finset H) (ρ : ℝ) (hρ : 0 ≤ ρ) :
    ∃ (n : ℕ), ∃ (C : Finset H), C ⊆ S ∧ IsRhoCoverFinset d C S ρ ∧ C.card = n := by
  -- S covers itself with ρ ≥ 0
  use S.card, S
  refine ⟨le_refl S, ?_, rfl⟩
  intro x hx
  use x, hx
  rw [hd_self x]
  exact hρ

/-- Internal covering number N(S, ρ, d): minimum cardinality of a ρ-cover with centers in S. -/
noncomputable def coveringNumber [DecidableEq H]
    (d : H → H → ℝ) (hd_self : ∀ x, d x x = 0) (S : Finset H) (ρ : ℝ) (hρ : 0 ≤ ρ) : ℕ :=
  open Classical in
  Nat.find (exists_cover_card d hd_self S ρ hρ)

theorem exists_separated_card (d : H → H → ℝ) (S : Finset H) (ρ : ℝ) :
    ∃ (n : ℕ), ∃ (C : Finset H), C ⊆ S ∧ IsRhoSeparated d C ρ ∧ C.card = n := by
  -- Empty set is separated
  use 0, ∅
  simp [IsRhoSeparated]

/-- Packing number P(S, ρ, d): maximum cardinality of a ρ-separated subset of S. -/
noncomputable def packingNumber [DecidableEq H]
    (d : H → H → ℝ) (S : Finset H) (ρ : ℝ) : ℕ :=
  open Classical in
  let separated_cards : Finset ℕ := (Finset.powerset S).filter (IsRhoSeparated d · ρ) |>.image Finset.card
  if h : separated_cards.Nonempty then separated_cards.max' h else 0

/-- Internal metric entropy H(S, ρ, d) = log₂ N(S, ρ, d). -/
noncomputable def metricEntropy [DecidableEq H]
    (d : H → H → ℝ) (hd_self : ∀ x, d x x = 0) (S : Finset H) (ρ : ℝ) (hρ : 0 ≤ ρ) : ℝ :=
  Real.log (coveringNumber d hd_self S ρ hρ : ℝ) / Real.log 2

/-- The set of points admitting a seen witness with `FCG ≤ L * ρ`. -/
def GoodFCGSet
    (R : E → ℝ) (hB : E → H) (d_repr : H → H → ℝ)
    (Seen : Set E) (L ρ : ℝ) : Set E :=
  {e | ∃ e0 ∈ Seen, FCG R hB d_repr e e0 ≤ L * ρ}

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
