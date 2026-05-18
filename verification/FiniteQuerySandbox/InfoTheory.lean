import Mathlib

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

/-!
# Finite Discrete Information Theory

Mathlib provides the finite-sum, real-logarithm, and probability infrastructure
used here. At the pinned Mathlib version, Shannon entropy and conditional mutual
information are not exported as the exact finite-discrete API needed by this
artifact, so we define those quantities locally by their standard finite PMF
formulas. The conditional DPI is proved here from finite KL nonnegativity and
the concrete conditional Markov factorization.
-/

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

/-- A finite discrete probability mass function over type `α`. -/
structure FinitePMF (α : Type) [Fintype α] [DecidableEq α] where
  pmf : α → ℝ
  pmf_nonneg : ∀ x, 0 ≤ pmf x
  sum_one : ∑ x : α, pmf x = 1

def FinitePMF.comapEquiv {η θ : Type} [Fintype η] [DecidableEq η] [Fintype θ]
    [DecidableEq θ] (e : θ ≃ η) (P : FinitePMF η) : FinitePMF θ where
  pmf x := P.pmf (e x)
  pmf_nonneg x := P.pmf_nonneg (e x)
  sum_one := by
    calc
      ∑ x : θ, P.pmf (e x) = ∑ y : η, P.pmf y := Equiv.sum_comp e P.pmf
      _ = 1 := P.sum_one

/-- The finite Shannon summand `-p log₂ p`. Mathlib's `Real.log 0 = 0` convention
makes the zero-mass term evaluate to zero. -/
def negMulLog2 (p : ℝ) : ℝ :=
  -(p * (Real.log p / Real.log 2))

/-- Entropy of an arbitrary finite mass function, used for marginals. -/
def entropyOf {η : Type} [Fintype η] [DecidableEq η] (mass : η → ℝ) : ℝ :=
  ∑ x : η, negMulLog2 (mass x)

/-- Shannon entropy of a finite PMF, in bits. -/
def entropy (P : FinitePMF α) : ℝ :=
  entropyOf P.pmf

/-! ## Basic positivity lemmas -/

lemma negMulLog2_nonneg {p : ℝ} (hp_nonneg : 0 ≤ p) (hp_le_one : p ≤ 1) :
    0 ≤ negMulLog2 p := by
  unfold negMulLog2
  by_cases hp : p = 0
  · simp [hp]
  · have hp_pos : 0 < p := lt_of_le_of_ne hp_nonneg (Ne.symm hp)
    have hlog_le : Real.log p ≤ 0 :=
      (Real.log_le_sub_one_of_pos hp_pos).trans (by linarith : p - 1 ≤ 0)
    have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
    have h_div_le : Real.log p / Real.log 2 ≤ 0 :=
      div_nonpos_of_nonpos_of_nonneg hlog_le hlog2_pos.le
    have h_prod_le : p * (Real.log p / Real.log 2) ≤ 0 :=
      mul_nonpos_of_nonneg_of_nonpos hp_nonneg h_div_le
    linarith

lemma pmf_le_one (P : FinitePMF α) (x : α) :
    P.pmf x ≤ 1 := by
  have h_nonneg : ∀ y, 0 ≤ P.pmf y := P.pmf_nonneg
  have : P.pmf x ≤ ∑ y : α, P.pmf y :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ x)
  linarith [P.sum_one]

lemma entropy_nonneg (P : FinitePMF α) :
    0 ≤ entropy P := by
  unfold entropy entropyOf
  exact Finset.sum_nonneg (fun x _ => negMulLog2_nonneg (P.pmf_nonneg x) (pmf_le_one P x))

lemma entropyOf_equiv_eq {η θ : Type} [Fintype η] [DecidableEq η] [Fintype θ]
    [DecidableEq θ] (e : η ≃ θ) (f : η → ℝ) (g : θ → ℝ)
    (h : ∀ x, f x = g (e x)) :
    entropyOf f = entropyOf g := by
  unfold entropyOf
  calc
    ∑ x : η, negMulLog2 (f x)
        = ∑ x : η, negMulLog2 (g (e x)) := by
          refine Finset.sum_congr rfl (fun x _ => ?_)
          rw [h x]
    _ = ∑ y : θ, negMulLog2 (g y) := Equiv.sum_comp e (fun y => negMulLog2 (g y))

lemma entropyOf_mul_log2 {η : Type} [Fintype η] [DecidableEq η] (mass : η → ℝ) :
    entropyOf mass * Real.log 2 = -∑ x : η, mass x * Real.log (mass x) := by
  unfold entropyOf negMulLog2
  have hlog2_ne_zero : Real.log 2 ≠ 0 := by positivity
  rw [Finset.sum_mul]
  calc
    ∑ x : η, (-(mass x * (Real.log (mass x) / Real.log 2))) * Real.log 2
        = ∑ x : η, -(mass x * Real.log (mass x)) := by
          refine Finset.sum_congr rfl (fun x _ => ?_)
          field_simp [hlog2_ne_zero]
    _ = -∑ x : η, mass x * Real.log (mass x) := by
          rw [← Finset.sum_neg_distrib]

/-! ### Marginal definitions and lemmas -/

def marginalLeftMass (P : FinitePMF (α × β)) (x : α) : ℝ :=
  ∑ y : β, P.pmf (x, y)

def marginalRightMass (P : FinitePMF (α × β)) (y : β) : ℝ :=
  ∑ x : α, P.pmf (x, y)

lemma marginalLeftMass_nonneg (P : FinitePMF (α × β)) (x : α) :
    0 ≤ marginalLeftMass P x :=
  Finset.sum_nonneg (fun y _ => P.pmf_nonneg (x, y))

lemma marginalRightMass_nonneg (P : FinitePMF (α × β)) (y : β) :
    0 ≤ marginalRightMass P y :=
  Finset.sum_nonneg (fun x _ => P.pmf_nonneg (x, y))

lemma marginalLeftMass_sum_one (P : FinitePMF (α × β)) :
    ∑ x : α, marginalLeftMass P x = 1 := by
  unfold marginalLeftMass
  rw [← Fintype.sum_prod_type]
  exact P.sum_one

lemma marginalRightMass_sum_one (P : FinitePMF (α × β)) :
    ∑ y : β, marginalRightMass P y = 1 := by
  unfold marginalRightMass
  rw [Finset.sum_comm]
  rw [← Fintype.sum_prod_type]
  exact P.sum_one

/--
Marginalize a leaf coordinate from a product-state PMF.  In the DAG proof this
is the PMF on the remaining subgraph after summing out a leaf variable.
-/
def marginalizeLeafPMF (P : FinitePMF (α × β)) : FinitePMF α where
  pmf x := ∑ leaf : β, P.pmf (x, leaf)
  pmf_nonneg x := by
    exact Finset.sum_nonneg fun leaf _ => P.pmf_nonneg (x, leaf)
  sum_one := by
    calc
      ∑ x : α, ∑ leaf : β, P.pmf (x, leaf)
          = ∑ p : α × β, P.pmf p := by
            rw [← Fintype.sum_prod_type]
      _ = 1 := P.sum_one

/--
Helper lemma for the leaf-marginalization step in the DAG Markov proof:
the subgraph PMF at a remaining assignment is exactly the sum of the original
joint PMF over the leaf coordinate.
-/
lemma sum_leaf_pmf_eq_subgraph_pmf (P : FinitePMF (α × β)) (x : α) :
    (∑ leaf : β, P.pmf (x, leaf)) = (marginalizeLeafPMF P).pmf x := by
  rfl

lemma marginalLeftMass_le_one (P : FinitePMF (α × β)) (x : α) :
    marginalLeftMass P x ≤ 1 := by
  have h_nonneg : ∀ x, 0 ≤ marginalLeftMass P x := marginalLeftMass_nonneg P
  have : marginalLeftMass P x ≤ ∑ x : α, marginalLeftMass P x :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ x)
  linarith [marginalLeftMass_sum_one P]

lemma marginalRightMass_le_one (P : FinitePMF (α × β)) (y : β) :
    marginalRightMass P y ≤ 1 := by
  have h_nonneg : ∀ y, 0 ≤ marginalRightMass P y := marginalRightMass_nonneg P
  have : marginalRightMass P y ≤ ∑ y : β, marginalRightMass P y :=
    Finset.single_le_sum (fun y' _ => h_nonneg y') (Finset.mem_univ y)
  linarith [marginalRightMass_sum_one P]

lemma pmf_le_marginalLeftMass (P : FinitePMF (α × β)) (x : α) (y : β) :
    P.pmf (x, y) ≤ marginalLeftMass P x := by
  unfold marginalLeftMass
  exact Finset.single_le_sum (fun y' _ => P.pmf_nonneg (x, y')) (Finset.mem_univ y)

lemma pmf_le_marginalRightMass (P : FinitePMF (α × β)) (x : α) (y : β) :
    P.pmf (x, y) ≤ marginalRightMass P y := by
  unfold marginalRightMass
  exact Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', y)) (Finset.mem_univ x)

/-! ## KL nonnegativity and entropy bounds -/

lemma Fintype.card_pos_of_finitePMF (P : FinitePMF α) :
    0 < Fintype.card α := by
  by_contra h
  push Not at h
  have hcard0 : Fintype.card α = 0 := by
    have h1 : Fintype.card α ≤ 0 := by linarith
    exact Nat.eq_zero_of_le_zero h1
  have hempty : IsEmpty α := Fintype.card_eq_zero_iff.mp hcard0
  have hempty2 : ∀ x : α, False := fun x => IsEmpty.false x
  have hsum0 : ∑ x : α, P.pmf x = 0 := by
    rw [Finset.sum_eq_zero]
    intro x _
    exact False.elim (hempty2 x)
  linarith [P.sum_one, hsum0]

lemma kl_nonneg {α : Type} [Fintype α] [DecidableEq α]
    (p q : α → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x)
    (hq_pos : ∀ x, 0 < q x)
    (hp_sum : ∑ x, p x = 1)
    (hq_sum : ∑ x, q x = 1) :
    0 ≤ ∑ x, p x * Real.log (p x / q x) := by
  have h_term : ∀ x, p x * Real.log (p x / q x) ≥ p x - q x := by
    intro x
    by_cases hpx : p x = 0
    · -- p x = 0: LHS = 0 * log(0) = 0, need 0 ≥ -q x
      rw [hpx]
      have h0 : (0 : ℝ) / q x = 0 := by simp
      simp [h0]
      linarith [hq_pos x]
    · -- p x > 0
      have hpx_pos : 0 < p x := lt_of_le_of_ne (hp_nonneg x) (Ne.symm hpx)
      have h1 : Real.log (q x / p x) ≤ q x / p x - 1 :=
        Real.log_le_sub_one_of_pos (div_pos (hq_pos x) hpx_pos)
      have h2 : p x * Real.log (q x / p x) ≤ q x - p x := by
        have h_mul : p x * (q x / p x - 1) = q x - p x := by
          field_simp [hpx_pos.ne']
        have h3 : p x * Real.log (q x / p x) ≤ p x * (q x / p x - 1) := by
          apply mul_le_mul_of_nonneg_left h1 (le_of_lt hpx_pos)
        linarith [h3, h_mul]
      have h3 : p x * Real.log (p x / q x) = -(p x * Real.log (q x / p x)) := by
        rw [← mul_neg]
        congr
        rw [show Real.log (p x / q x) = -Real.log (q x / p x) by
          rw [Real.log_div (by exact hpx_pos.ne') (by exact (hq_pos x).ne')]
          rw [Real.log_div (by exact (hq_pos x).ne') (by exact hpx_pos.ne')]
          ring]
      rw [h3]
      linarith [h2]
  have hsum : ∑ x, p x * Real.log (p x / q x) ≥ ∑ x, (p x - q x) := by
    apply Finset.sum_le_sum
    intro x _
    exact h_term x
  have h_eq : ∑ x, (p x - q x) = 0 := by
    rw [Finset.sum_sub_distrib]
    linarith [hp_sum, hq_sum]
  linarith [hsum, h_eq]

lemma kl_nonneg_support {ι : Type} [Fintype ι] [DecidableEq ι]
    (p q : ι → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x)
    (hq_nonneg : ∀ x, 0 ≤ q x)
    (h_support : ∀ x, p x ≠ 0 → 0 < q x)
    (hp_sum : ∑ x, p x = 1)
    (hq_sum : ∑ x, q x = 1) :
    0 ≤ ∑ x, p x * Real.log (p x / q x) := by
  have h_term : ∀ x, p x * Real.log (p x / q x) ≥ p x - q x := by
    intro x
    by_cases hpx : p x = 0
    · rw [hpx]
      have h0 : (0 : ℝ) / q x = 0 := by simp
      simp [h0]
      linarith [hq_nonneg x]
    · have hpx_pos : 0 < p x := lt_of_le_of_ne (hp_nonneg x) (Ne.symm hpx)
      have hqx_pos : 0 < q x := h_support x hpx
      have h1 : Real.log (q x / p x) ≤ q x / p x - 1 :=
        Real.log_le_sub_one_of_pos (div_pos hqx_pos hpx_pos)
      have h2 : p x * Real.log (q x / p x) ≤ q x - p x := by
        have h_mul : p x * (q x / p x - 1) = q x - p x := by
          field_simp [hpx_pos.ne']
        have h3 : p x * Real.log (q x / p x) ≤ p x * (q x / p x - 1) := by
          apply mul_le_mul_of_nonneg_left h1 (le_of_lt hpx_pos)
        linarith [h3, h_mul]
      have h3 : p x * Real.log (p x / q x) = -(p x * Real.log (q x / p x)) := by
        rw [← mul_neg]
        congr
        rw [show Real.log (p x / q x) = -Real.log (q x / p x) by
          rw [Real.log_div (by exact hpx_pos.ne') (by exact hqx_pos.ne')]
          rw [Real.log_div (by exact hqx_pos.ne') (by exact hpx_pos.ne')]
          ring]
      rw [h3]
      linarith [h2]
  have hsum : ∑ x, p x * Real.log (p x / q x) ≥ ∑ x, (p x - q x) := by
    apply Finset.sum_le_sum
    intro x _
    exact h_term x
  have h_eq : ∑ x, (p x - q x) = 0 := by
    rw [Finset.sum_sub_distrib]
    linarith [hp_sum, hq_sum]
  linarith [hsum, h_eq]

lemma entropy_le_log_card (P : FinitePMF α) :
    entropy P ≤ Real.log (Fintype.card α) / Real.log 2 := by
  let q : α → ℝ := fun _ => 1 / Fintype.card α
  have hcard_pos : 0 < Fintype.card α := Fintype.card_pos_of_finitePMF P
  have hcard_real_pos : (0 : ℝ) < (Fintype.card α : ℝ) := by exact_mod_cast hcard_pos
  have hq_pos : ∀ x, 0 < q x := fun _ => by positivity
  have hq_sum : ∑ x, q x = 1 := by
    simp [q]
    field_simp [hcard_real_pos.ne']
  have h_kl := kl_nonneg P.pmf q P.pmf_nonneg hq_pos P.sum_one hq_sum
  have h_kl_expanded : ∑ x, P.pmf x * Real.log (P.pmf x / q x)
      = - (entropy P * Real.log 2) + Real.log (Fintype.card α) := by
    have h1 : ∀ x, P.pmf x * Real.log (P.pmf x / q x)
        = P.pmf x * Real.log (P.pmf x) + P.pmf x * Real.log (Fintype.card α) := by
      intro x
      have h_div : P.pmf x / q x = P.pmf x * (Fintype.card α : ℝ) := by
        simp [q]
      rw [h_div]
      by_cases hx : P.pmf x = 0
      · simp [hx]
      · rw [Real.log_mul (by exact hx) (by exact hcard_real_pos.ne')]
        ring
    have h2 : ∑ x, P.pmf x * Real.log (P.pmf x / q x)
        = ∑ x, (P.pmf x * Real.log (P.pmf x) + P.pmf x * Real.log (Fintype.card α)) := by
      apply Finset.sum_congr rfl
      intro x _
      exact h1 x
    rw [h2]
    rw [Finset.sum_add_distrib]
    have h3 : ∑ x : α, P.pmf x * Real.log (Fintype.card α) = Real.log (Fintype.card α) := by
      have h_const : ∑ x : α, P.pmf x * Real.log (Fintype.card α)
          = Real.log (Fintype.card α) * ∑ x : α, P.pmf x := by
        rw [Finset.mul_sum]
        simp [mul_comm]
      rw [h_const, P.sum_one]
      ring
    have h4 : ∑ x : α, P.pmf x * Real.log (P.pmf x) = - (entropy P * Real.log 2) := by
      have h5 : entropy P = ∑ x : α, -(P.pmf x * (Real.log (P.pmf x) / Real.log 2)) := by
        unfold entropy entropyOf negMulLog2
        rfl
      rw [h5]
      have hlog2_ne_zero : Real.log 2 ≠ 0 := by positivity
      have h6 : ∀ x, P.pmf x * Real.log (P.pmf x)
          = (-(P.pmf x * (Real.log (P.pmf x) / Real.log 2))) * (-Real.log 2) := by
        intro x
        field_simp [hlog2_ne_zero]
      simp_rw [h6]
      rw [← Finset.sum_mul]
      ring
    rw [h3, h4]
  rw [h_kl_expanded] at h_kl
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  have h_mul : entropy P * Real.log 2 ≤ Real.log (Fintype.card α) := by linarith [h_kl]
  have h_div : entropy P ≤ Real.log (Fintype.card α) / Real.log 2 := by
    apply (le_div_iff₀ (by positivity)).mpr
    linarith [h_mul]
  exact h_div

def marginalXZMass (P : FinitePMF (α × β × γ)) (xz : α × γ) : ℝ :=
  ∑ y : β, P.pmf (xz.1, y, xz.2)

def marginalYZMass (P : FinitePMF (α × β × γ)) (yz : β × γ) : ℝ :=
  ∑ x : α, P.pmf (x, yz.1, yz.2)

def marginalZMass (P : FinitePMF (α × β × γ)) (z : γ) : ℝ :=
  ∑ x : α, ∑ y : β, P.pmf (x, y, z)

/-- Finite conditional mutual information `I(X;Y | Z)`. -/
def condMutualInfo (P_XYZ : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalXZMass P_XYZ) +
    entropyOf (marginalYZMass P_XYZ) -
    entropyOf (marginalZMass P_XYZ) -
    entropyOf (fun xyz : α × β × γ => P_XYZ.pmf xyz)

/-- Finite conditional entropy `H(X | Y) = H(X,Y) - H(Y)`. -/
def condEntropy (P_XY : FinitePMF (α × β)) : ℝ :=
  entropyOf (fun xy : α × β => P_XY.pmf xy) -
    entropyOf (marginalRightMass P_XY)

/-- Mutual information I(X;Y) for a 2-variable PMF. -/
def mutualInfo (P : FinitePMF (α × β)) : ℝ :=
  entropyOf (marginalLeftMass P) + entropyOf (marginalRightMass P) - entropyOf P.pmf

/-- Product of marginals P_X * P_Y as a reference distribution. -/
def productMarginalMass (P : FinitePMF (α × β)) (xy : α × β) : ℝ :=
  marginalLeftMass P xy.1 * marginalRightMass P xy.2

lemma productMarginalMass_nonneg (P : FinitePMF (α × β)) (xy : α × β) :
    0 ≤ productMarginalMass P xy :=
  mul_nonneg (marginalLeftMass_nonneg P xy.1) (marginalRightMass_nonneg P xy.2)

lemma productMarginalMass_pos_of_pmf_ne_zero
    (P : FinitePMF (α × β)) (xy : α × β)
    (hxy : P.pmf xy ≠ 0) :
    0 < productMarginalMass P xy := by
  have h_left : 0 < marginalLeftMass P xy.1 :=
    lt_of_lt_of_le (lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy))
      (Finset.single_le_sum (fun y' _ => P.pmf_nonneg (xy.1, y')) (Finset.mem_univ xy.2))
  have h_right : 0 < marginalRightMass P xy.2 :=
    lt_of_lt_of_le (lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy))
      (Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', xy.2)) (Finset.mem_univ xy.1))
  exact mul_pos h_left h_right

lemma productMarginalMass_sum_one (P : FinitePMF (α × β)) :
    ∑ xy : α × β, productMarginalMass P xy = 1 := by
  unfold productMarginalMass
  calc
    ∑ xy : α × β, marginalLeftMass P xy.1 * marginalRightMass P xy.2
        = ∑ x : α, ∑ y : β, marginalLeftMass P x * marginalRightMass P y := by
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, (marginalLeftMass P x * ∑ y : β, marginalRightMass P y) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.mul_sum]
    _ = ∑ x : α, marginalLeftMass P x * 1 := by
          rw [marginalRightMass_sum_one]
    _ = 1 := by
          simp
          exact marginalLeftMass_sum_one P

lemma sum_pmf_log_marginalLeftMass (P : FinitePMF (α × β)) :
    (∑ xy : α × β, P.pmf xy * Real.log (marginalLeftMass P xy.1))
      =
    ∑ x : α, marginalLeftMass P x * Real.log (marginalLeftMass P x) := by
  calc
    (∑ xy : α × β, P.pmf xy * Real.log (marginalLeftMass P xy.1))
        = ∑ x : α, ∑ y : β, P.pmf (x, y) * Real.log (marginalLeftMass P x) := by
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, (∑ y : β, P.pmf (x, y)) * Real.log (marginalLeftMass P x) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [← Finset.sum_mul]
    _ = ∑ x : α, marginalLeftMass P x * Real.log (marginalLeftMass P x) := rfl

lemma sum_pmf_log_marginalRightMass (P : FinitePMF (α × β)) :
    (∑ xy : α × β, P.pmf xy * Real.log (marginalRightMass P xy.2))
      =
    ∑ y : β, marginalRightMass P y * Real.log (marginalRightMass P y) := by
  calc
    (∑ xy : α × β, P.pmf xy * Real.log (marginalRightMass P xy.2))
        = ∑ x : α, ∑ y : β, P.pmf (x, y) * Real.log (marginalRightMass P y) := by
          rw [Fintype.sum_prod_type]
    _ = ∑ y : β, ∑ x : α, P.pmf (x, y) * Real.log (marginalRightMass P y) := by
          rw [Finset.sum_comm]
    _ = ∑ y : β, (∑ x : α, P.pmf (x, y)) * Real.log (marginalRightMass P y) := by
          apply Finset.sum_congr rfl
          intro y _
          rw [← Finset.sum_mul]
    _ = ∑ y : β, marginalRightMass P y * Real.log (marginalRightMass P y) := rfl

lemma condEntropy_mul_log2 (P : FinitePMF (α × β)) :
    condEntropy P * Real.log 2 =
      ∑ xy : α × β, P.pmf xy * Real.log (marginalRightMass P xy.2 / P.pmf xy) := by
  have hJoint := entropyOf_mul_log2 (fun xy : α × β => P.pmf xy)
  have hMarg := entropyOf_mul_log2 (marginalRightMass P)
  unfold condEntropy
  calc
    (entropyOf (fun xy : α × β => P.pmf xy) - entropyOf (marginalRightMass P)) * Real.log 2
        = entropyOf (fun xy : α × β => P.pmf xy) * Real.log 2 -
            entropyOf (marginalRightMass P) * Real.log 2 := by ring
    _ = (-∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy)) -
          (-∑ y : β, marginalRightMass P y * Real.log (marginalRightMass P y)) := by
          rw [hJoint, hMarg]
    _ = -∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy) +
          ∑ xy : α × β, P.pmf xy * Real.log (marginalRightMass P xy.2) := by
          rw [sum_pmf_log_marginalRightMass P]
          ring
    _ = ∑ xy : α × β,
          (P.pmf xy * Real.log (marginalRightMass P xy.2) -
            P.pmf xy * Real.log (P.pmf xy)) := by
          rw [Finset.sum_sub_distrib]
          ring
    _ = ∑ xy : α × β,
          P.pmf xy * Real.log (marginalRightMass P xy.2 / P.pmf xy) := by
          apply Finset.sum_congr rfl
          intro xy _
          by_cases hxy : P.pmf xy = 0
          · simp [hxy]
          · have hp_pos : 0 < P.pmf xy :=
              lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy)
            have hm_pos : 0 < marginalRightMass P xy.2 :=
              lt_of_lt_of_le hp_pos (pmf_le_marginalRightMass P xy.1 xy.2)
            rw [Real.log_div hm_pos.ne' hp_pos.ne']
            ring

lemma condEntropy_nonneg (P : FinitePMF (α × β)) :
    0 ≤ condEntropy P := by
  have hmul_eq := condEntropy_mul_log2 (P := P)
  have hsum_nonneg :
      0 ≤ ∑ xy : α × β,
        P.pmf xy * Real.log (marginalRightMass P xy.2 / P.pmf xy) := by
    apply Finset.sum_nonneg
    intro xy _
    by_cases hxy : P.pmf xy = 0
    · simp [hxy]
    · have hp_pos : 0 < P.pmf xy :=
        lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy)
      have hle : P.pmf xy ≤ marginalRightMass P xy.2 :=
        pmf_le_marginalRightMass P xy.1 xy.2
      have hratio_ge_one : 1 ≤ marginalRightMass P xy.2 / P.pmf xy := by
        rw [le_div_iff₀ hp_pos]
        simpa using hle
      exact mul_nonneg hp_pos.le (Real.log_nonneg hratio_ge_one)
  have hmul_nonneg : 0 ≤ condEntropy P * Real.log 2 := by
    rw [hmul_eq]
    exact hsum_nonneg
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  by_contra hneg
  push Not at hneg
  have hmul_neg : condEntropy P * Real.log 2 < 0 :=
    mul_neg_of_neg_of_pos hneg hlog2_pos
  linarith

lemma mutualInfo_kl_identity (P : FinitePMF (α × β)) :
    (∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy))
    = mutualInfo P * Real.log 2 := by
  let A : ℝ := ∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy)
  let B : ℝ := ∑ x : α, marginalLeftMass P x * Real.log (marginalLeftMass P x)
  let C : ℝ := ∑ y : β, marginalRightMass P y * Real.log (marginalRightMass P y)
  have hterm : ∀ xy : α × β,
      P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy)
        =
      P.pmf xy * Real.log (P.pmf xy) - P.pmf xy * Real.log (marginalLeftMass P xy.1)
        - P.pmf xy * Real.log (marginalRightMass P xy.2) := by
    intro xy
    by_cases hxy : P.pmf xy = 0
    · simp [hxy]
    · have hp_pos : 0 < P.pmf xy := lt_of_le_of_ne (P.pmf_nonneg xy) (Ne.symm hxy)
      have h_left_pos : 0 < marginalLeftMass P xy.1 :=
        lt_of_lt_of_le hp_pos (Finset.single_le_sum (fun y' _ => P.pmf_nonneg (xy.1, y')) (Finset.mem_univ xy.2))
      have h_right_pos : 0 < marginalRightMass P xy.2 :=
        lt_of_lt_of_le hp_pos (Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', xy.2)) (Finset.mem_univ xy.1))
      have hq_pos : 0 < productMarginalMass P xy := mul_pos h_left_pos h_right_pos
      rw [Real.log_div hp_pos.ne' hq_pos.ne']
      unfold productMarginalMass
      rw [Real.log_mul h_left_pos.ne' h_right_pos.ne']
      ring
  have hsum :
      (∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy))
        = A - B - C := by
    calc
      (∑ xy : α × β, P.pmf xy * Real.log (P.pmf xy / productMarginalMass P xy))
          = ∑ xy : α × β, (P.pmf xy * Real.log (P.pmf xy) - P.pmf xy * Real.log (marginalLeftMass P xy.1)
              - P.pmf xy * Real.log (marginalRightMass P xy.2)) := by
            apply Finset.sum_congr rfl
            intro xy _
            exact hterm xy
      _ = A - B - C := by
            rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib]
            rw [sum_pmf_log_marginalLeftMass P, sum_pmf_log_marginalRightMass P]
  have hHL := entropyOf_mul_log2 (marginalLeftMass P)
  have hHR := entropyOf_mul_log2 (marginalRightMass P)
  have hHFull := entropyOf_mul_log2 P.pmf
  have hmi : mutualInfo P * Real.log 2 = A - B - C := by
    unfold mutualInfo
    calc
      (entropyOf (marginalLeftMass P) + entropyOf (marginalRightMass P) - entropyOf P.pmf) * Real.log 2
          = entropyOf (marginalLeftMass P) * Real.log 2 + entropyOf (marginalRightMass P) * Real.log 2
              - entropyOf P.pmf * Real.log 2 := by ring
      _ = A - B - C := by
            rw [hHL, hHR, hHFull]
            simp [A, B, C]
            ring
  rw [hsum, hmi]

lemma mutualInfo_nonneg (P : FinitePMF (α × β)) :
    0 ≤ mutualInfo P := by
  have hkl := kl_nonneg_support P.pmf (productMarginalMass P)
    P.pmf_nonneg
    (productMarginalMass_nonneg P)
    (productMarginalMass_pos_of_pmf_ne_zero P)
    P.sum_one
    (productMarginalMass_sum_one P)
  rw [mutualInfo_kl_identity P] at hkl
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  by_contra hneg
  push Not at hneg
  have hmul_neg : mutualInfo P * Real.log 2 < 0 :=
    mul_neg_of_neg_of_pos hneg hlog2_pos
  linarith

def condEntropy_Z_W (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalXZMass P) - entropyOf (marginalZMass P)

lemma condMutualInfo_le_condEntropy_Z_W (P : FinitePMF (α × β × γ)) :
    condMutualInfo P ≤ condEntropy_Z_W P := by
  unfold condMutualInfo condEntropy_Z_W
  have h_nonneg : 0 ≤ entropyOf (fun xyz : α × β × γ => P.pmf xyz) - entropyOf (marginalYZMass P) := by
    have h := condEntropy_nonneg (P := P)
    simpa [condEntropy, marginalRightMass, marginalYZMass] using h
  linarith

lemma marginalXZMass_nonneg (P : FinitePMF (α × β × γ)) (xz : α × γ) :
    0 ≤ marginalXZMass P xz :=
  Finset.sum_nonneg (fun y _ => P.pmf_nonneg (xz.1, y, xz.2))

lemma marginalYZMass_nonneg (P : FinitePMF (α × β × γ)) (yz : β × γ) :
    0 ≤ marginalYZMass P yz :=
  Finset.sum_nonneg (fun x _ => P.pmf_nonneg (x, yz.1, yz.2))

lemma marginalZMass_nonneg (P : FinitePMF (α × β × γ)) (z : γ) :
    0 ≤ marginalZMass P z :=
  Finset.sum_nonneg (fun x _ => Finset.sum_nonneg (fun y _ => P.pmf_nonneg (x, y, z)))

lemma marginalXZMass_sum_z (P : FinitePMF (α × β × γ)) (z : γ) :
    ∑ x : α, marginalXZMass P (x, z) = marginalZMass P z := by
  rfl

lemma marginalYZMass_sum_z (P : FinitePMF (α × β × γ)) (z : γ) :
    ∑ y : β, marginalYZMass P (y, z) = marginalZMass P z := by
  unfold marginalYZMass marginalZMass
  rw [Finset.sum_comm]

lemma marginalZMass_sum_one (P : FinitePMF (α × β × γ)) :
    ∑ z : γ, marginalZMass P z = 1 := by
  have hsum : (∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z)) = 1 := by
    calc
      (∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z))
          = ∑ x : α, ∑ yz : β × γ, P.pmf (x, yz.1, yz.2) := by
            apply Finset.sum_congr rfl
            intro x _
            rw [← Fintype.sum_prod_type' (fun y z => P.pmf (x, y, z))]
      _ = ∑ xyz : α × β × γ, P.pmf xyz := by
            rw [← Fintype.sum_prod_type]
      _ = 1 := P.sum_one
  unfold marginalZMass
  rw [Finset.sum_comm]
  rw [show (∑ x : α, ∑ z : γ, ∑ y : β, P.pmf (x, y, z))
      = ∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z) by
        apply Finset.sum_congr rfl
        intro x _
        rw [Finset.sum_comm]]
  exact hsum

lemma pmf_le_marginalXZMass (P : FinitePMF (α × β × γ)) (x : α) (y : β) (z : γ) :
    P.pmf (x, y, z) ≤ marginalXZMass P (x, z) := by
  unfold marginalXZMass
  exact Finset.single_le_sum (fun y' _ => P.pmf_nonneg (x, y', z)) (Finset.mem_univ y)

lemma pmf_le_marginalYZMass (P : FinitePMF (α × β × γ)) (x : α) (y : β) (z : γ) :
    P.pmf (x, y, z) ≤ marginalYZMass P (y, z) := by
  unfold marginalYZMass
  exact Finset.single_le_sum (fun x' _ => P.pmf_nonneg (x', y, z)) (Finset.mem_univ x)

lemma marginalXZMass_le_marginalZMass (P : FinitePMF (α × β × γ)) (x : α) (z : γ) :
    marginalXZMass P (x, z) ≤ marginalZMass P z := by
  have h_nonneg : ∀ x : α, 0 ≤ marginalXZMass P (x, z) :=
    fun x => marginalXZMass_nonneg P (x, z)
  have hle : marginalXZMass P (x, z) ≤ ∑ x : α, marginalXZMass P (x, z) :=
    Finset.single_le_sum (fun x _ => h_nonneg x) (Finset.mem_univ x)
  rwa [marginalXZMass_sum_z P z] at hle

lemma marginalYZMass_le_marginalZMass (P : FinitePMF (α × β × γ)) (y : β) (z : γ) :
    marginalYZMass P (y, z) ≤ marginalZMass P z := by
  have h_nonneg : ∀ y : β, 0 ≤ marginalYZMass P (y, z) :=
    fun y => marginalYZMass_nonneg P (y, z)
  have hle : marginalYZMass P (y, z) ≤ ∑ y : β, marginalYZMass P (y, z) :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ y)
  rwa [marginalYZMass_sum_z P z] at hle

def condProductMass (P : FinitePMF (α × β × γ)) (xyz : α × β × γ) : ℝ :=
  marginalXZMass P (xyz.1, xyz.2.2) *
    marginalYZMass P (xyz.2.1, xyz.2.2) /
    marginalZMass P xyz.2.2

lemma condProductMass_nonneg (P : FinitePMF (α × β × γ)) (xyz : α × β × γ) :
    0 ≤ condProductMass P xyz := by
  unfold condProductMass
  exact div_nonneg
    (mul_nonneg (marginalXZMass_nonneg P (xyz.1, xyz.2.2))
      (marginalYZMass_nonneg P (xyz.2.1, xyz.2.2)))
    (marginalZMass_nonneg P xyz.2.2)

lemma condProductMass_pos_of_pmf_ne_zero
    (P : FinitePMF (α × β × γ)) (xyz : α × β × γ)
    (hxyz : P.pmf xyz ≠ 0) :
    0 < condProductMass P xyz := by
  rcases xyz with ⟨x, y, z⟩
  have hp_pos : 0 < P.pmf (x, y, z) :=
    lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
  have hxz_pos : 0 < marginalXZMass P (x, z) :=
    lt_of_lt_of_le hp_pos (pmf_le_marginalXZMass P x y z)
  have hyz_pos : 0 < marginalYZMass P (y, z) :=
    lt_of_lt_of_le hp_pos (pmf_le_marginalYZMass P x y z)
  have hz_pos : 0 < marginalZMass P z :=
    lt_of_lt_of_le hxz_pos (marginalXZMass_le_marginalZMass P x z)
  unfold condProductMass
  exact div_pos (mul_pos hxz_pos hyz_pos) hz_pos

lemma condProductMass_sum_fiber (P : FinitePMF (α × β × γ)) (z : γ) :
    (∑ x : α, ∑ y : β, condProductMass P (x, y, z)) = marginalZMass P z := by
  by_cases hz : marginalZMass P z = 0
  · have hxz_zero : ∀ x : α, marginalXZMass P (x, z) = 0 := by
      intro x
      have hle := marginalXZMass_le_marginalZMass P x z
      have hnonneg := marginalXZMass_nonneg P (x, z)
      linarith
    simp [condProductMass, hz, hxz_zero]
  · have hz_pos : 0 < marginalZMass P z :=
      lt_of_le_of_ne (marginalZMass_nonneg P z) (Ne.symm hz)
    calc
      (∑ x : α, ∑ y : β, condProductMass P (x, y, z))
          = ∑ x : α, ∑ y : β,
              marginalXZMass P (x, z) * marginalYZMass P (y, z) /
                marginalZMass P z := by
            rfl
      _ = ∑ x : α, marginalXZMass P (x, z) := by
            apply Finset.sum_congr rfl
            intro x _
            have hterm : ∀ y : β,
                marginalXZMass P (x, z) * marginalYZMass P (y, z) /
                    marginalZMass P z
                  =
                (marginalXZMass P (x, z) / marginalZMass P z) *
                    marginalYZMass P (y, z) := by
              intro y
              field_simp [hz]
            simp_rw [hterm]
            rw [← Finset.mul_sum, marginalYZMass_sum_z P z]
            field_simp [hz]
      _ = marginalZMass P z := marginalXZMass_sum_z P z

lemma condProductMass_sum_one (P : FinitePMF (α × β × γ)) :
    ∑ xyz : α × β × γ, condProductMass P xyz = 1 := by
  calc
    ∑ xyz : α × β × γ, condProductMass P xyz
        = ∑ x : α, ∑ y : β, ∑ z : γ, condProductMass P (x, y, z) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β, condProductMass P (x, y, z) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ z : γ, ∑ x : α, ∑ y : β, condProductMass P (x, y, z) := by
          rw [Finset.sum_comm]
    _ = ∑ z : γ, marginalZMass P z := by
          apply Finset.sum_congr rfl
          intro z _
          exact condProductMass_sum_fiber P z
    _ = 1 := marginalZMass_sum_one P

lemma sum_pmf_log_marginalXZMass (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
      =
    ∑ xz : α × γ, marginalXZMass P xz * Real.log (marginalXZMass P xz) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalXZMass P (x, z)) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalXZMass P (x, z)) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ x : α, ∑ z : γ,
            marginalXZMass P (x, z) * Real.log (marginalXZMass P (x, z)) := by
          apply Finset.sum_congr rfl
          intro x _
          apply Finset.sum_congr rfl
          intro z _
          rw [← Finset.sum_mul]
          rfl
    _ = ∑ xz : α × γ, marginalXZMass P xz * Real.log (marginalXZMass P xz) := by
          rw [← Fintype.sum_prod_type' (fun x z =>
            marginalXZMass P (x, z) * Real.log (marginalXZMass P (x, z)))]

lemma sum_pmf_log_marginalYZMass (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
      =
    ∑ yz : β × γ, marginalYZMass P yz * Real.log (marginalYZMass P yz) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalYZMass P (y, z)) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ y : β, ∑ z : γ, ∑ x : α,
            P.pmf (x, y, z) * Real.log (marginalYZMass P (y, z)) := by
          rw [Finset.sum_comm]
          apply Finset.sum_congr rfl
          intro y _
          rw [Finset.sum_comm]
    _ = ∑ y : β, ∑ z : γ,
            marginalYZMass P (y, z) * Real.log (marginalYZMass P (y, z)) := by
          apply Finset.sum_congr rfl
          intro y _
          apply Finset.sum_congr rfl
          intro z _
          rw [← Finset.sum_mul]
          rfl
    _ = ∑ yz : β × γ, marginalYZMass P yz * Real.log (marginalYZMass P yz) := by
          rw [← Fintype.sum_prod_type' (fun y z =>
            marginalYZMass P (y, z) * Real.log (marginalYZMass P (y, z)))]

lemma sum_pmf_log_marginalZMass (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalZMass P xyz.2.2))
      =
    ∑ z : γ, marginalZMass P z * Real.log (marginalZMass P z) := by
  calc
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (marginalZMass P xyz.2.2))
        = ∑ x : α, ∑ y : β, ∑ z : γ,
            P.pmf (x, y, z) * Real.log (marginalZMass P z) := by
          rw [Fintype.sum_prod_type]
          congr with x
          rw [Fintype.sum_prod_type]
    _ = ∑ x : α, ∑ z : γ, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalZMass P z) := by
          apply Finset.sum_congr rfl
          intro x _
          rw [Finset.sum_comm]
    _ = ∑ z : γ, ∑ x : α, ∑ y : β,
            P.pmf (x, y, z) * Real.log (marginalZMass P z) := by
          rw [Finset.sum_comm]
    _ = ∑ z : γ,
            marginalZMass P z * Real.log (marginalZMass P z) := by
          apply Finset.sum_congr rfl
          intro z _
          rw [show (∑ x : α, ∑ y : β,
              P.pmf (x, y, z) * Real.log (marginalZMass P z))
              =
              ∑ x : α, (∑ y : β, P.pmf (x, y, z)) * Real.log (marginalZMass P z) by
                apply Finset.sum_congr rfl
                intro x _
                rw [← Finset.sum_mul]]
          rw [← Finset.sum_mul]
          rfl

lemma condMutualInfo_kl_identity (P : FinitePMF (α × β × γ)) :
    (∑ xyz : α × β × γ,
      P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz))
      =
    condMutualInfo P * Real.log 2 := by
  let A : ℝ := ∑ xyz : α × β × γ, P.pmf xyz * Real.log (P.pmf xyz)
  let B : ℝ := ∑ xz : α × γ, marginalXZMass P xz * Real.log (marginalXZMass P xz)
  let C : ℝ := ∑ yz : β × γ, marginalYZMass P yz * Real.log (marginalYZMass P yz)
  let D : ℝ := ∑ z : γ, marginalZMass P z * Real.log (marginalZMass P z)
  have hterm : ∀ xyz : α × β × γ,
      P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz)
        =
      ((P.pmf xyz * Real.log (P.pmf xyz)
        - P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
        - P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
        + P.pmf xyz * Real.log (marginalZMass P xyz.2.2) := by
    intro xyz
    by_cases hxyz : P.pmf xyz = 0
    · simp [hxyz]
    · rcases xyz with ⟨x, y, z⟩
      have hp_pos : 0 < P.pmf (x, y, z) :=
        lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
      have hxz_pos : 0 < marginalXZMass P (x, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalXZMass P x y z)
      have hyz_pos : 0 < marginalYZMass P (y, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalYZMass P x y z)
      have hz_pos : 0 < marginalZMass P z :=
        lt_of_lt_of_le hxz_pos (marginalXZMass_le_marginalZMass P x z)
      have hq_pos : 0 < condProductMass P (x, y, z) :=
        condProductMass_pos_of_pmf_ne_zero P (x, y, z) hxyz
      have hlogq : Real.log (condProductMass P (x, y, z))
          =
          Real.log (marginalXZMass P (x, z)) +
          Real.log (marginalYZMass P (y, z)) -
          Real.log (marginalZMass P z) := by
        unfold condProductMass
        rw [Real.log_div (mul_ne_zero hxz_pos.ne' hyz_pos.ne') hz_pos.ne']
        rw [Real.log_mul hxz_pos.ne' hyz_pos.ne']
      rw [Real.log_div hp_pos.ne' hq_pos.ne', hlogq]
      ring
  have hsum :
      (∑ xyz : α × β × γ,
        P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz))
        = A - B - C + D := by
    calc
      (∑ xyz : α × β × γ,
        P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz))
          =
        ∑ xyz : α × β × γ,
          (((P.pmf xyz * Real.log (P.pmf xyz)
            - P.pmf xyz * Real.log (marginalXZMass P (xyz.1, xyz.2.2)))
            - P.pmf xyz * Real.log (marginalYZMass P (xyz.2.1, xyz.2.2)))
            + P.pmf xyz * Real.log (marginalZMass P xyz.2.2)) := by
            apply Finset.sum_congr rfl
            intro xyz _
            exact hterm xyz
      _ = A - B - C + D := by
            rw [Finset.sum_add_distrib, Finset.sum_sub_distrib, Finset.sum_sub_distrib]
            rw [sum_pmf_log_marginalXZMass P, sum_pmf_log_marginalYZMass P,
              sum_pmf_log_marginalZMass P]
  have hHXZ := entropyOf_mul_log2 (marginalXZMass P)
  have hHYZ := entropyOf_mul_log2 (marginalYZMass P)
  have hHZ := entropyOf_mul_log2 (marginalZMass P)
  have hHXYZ := entropyOf_mul_log2 (fun xyz : α × β × γ => P.pmf xyz)
  have hcmi : condMutualInfo P * Real.log 2 = A - B - C + D := by
    unfold condMutualInfo
    calc
      (entropyOf (marginalXZMass P) + entropyOf (marginalYZMass P) -
          entropyOf (marginalZMass P) -
          entropyOf (fun xyz : α × β × γ => P.pmf xyz)) * Real.log 2
          =
        entropyOf (marginalXZMass P) * Real.log 2 +
          entropyOf (marginalYZMass P) * Real.log 2 -
          entropyOf (marginalZMass P) * Real.log 2 -
          entropyOf (fun xyz : α × β × γ => P.pmf xyz) * Real.log 2 := by
            ring
      _ = A - B - C + D := by
            rw [hHXZ, hHYZ, hHZ, hHXYZ]
            simp [A, B, C, D]
            ring
  rw [hsum, hcmi]

lemma condMutualInfo_nonneg (P : FinitePMF (α × β × γ)) :
    0 ≤ condMutualInfo P := by
  have hkl := kl_nonneg_support P.pmf (condProductMass P)
    P.pmf_nonneg
    (condProductMass_nonneg P)
    (condProductMass_pos_of_pmf_ne_zero P)
    P.sum_one
    (condProductMass_sum_one P)
  rw [condMutualInfo_kl_identity P] at hkl
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  by_contra hneg
  push Not at hneg
  have hmul_neg : condMutualInfo P * Real.log 2 < 0 :=
    mul_neg_of_neg_of_pos hneg hlog2_pos
  linarith

lemma condMutualInfo_eq_zero_of_condIndep
    (P : FinitePMF (α × β × γ))
    (h : ∀ x y z,
      P.pmf (x, y, z) * marginalZMass P z =
        marginalXZMass P (x, z) * marginalYZMass P (y, z)) :
    condMutualInfo P = 0 := by
  have hkl_zero :
      (∑ xyz : α × β × γ,
        P.pmf xyz * Real.log (P.pmf xyz / condProductMass P xyz)) = 0 := by
    apply Finset.sum_eq_zero
    intro xyz _
    by_cases hxyz : P.pmf xyz = 0
    · simp [hxyz]
    · rcases xyz with ⟨x, y, z⟩
      have hp_pos : 0 < P.pmf (x, y, z) :=
        lt_of_le_of_ne (P.pmf_nonneg (x, y, z)) (Ne.symm hxyz)
      have hxz_pos : 0 < marginalXZMass P (x, z) :=
        lt_of_lt_of_le hp_pos (pmf_le_marginalXZMass P x y z)
      have hz_pos : 0 < marginalZMass P z :=
        lt_of_lt_of_le hxz_pos (marginalXZMass_le_marginalZMass P x z)
      have hq_eq : condProductMass P (x, y, z) = P.pmf (x, y, z) := by
        unfold condProductMass
        rw [← h x y z]
        field_simp [hz_pos.ne']
      rw [hq_eq]
      simp [hxyz]
  have hmul : condMutualInfo P * Real.log 2 = 0 := by
    rw [← condMutualInfo_kl_identity P, hkl_zero]
  have hlog2_ne : Real.log 2 ≠ 0 := by positivity
  exact (mul_eq_zero.mp hmul).resolve_right hlog2_ne

def marginalXWMass (P : FinitePMF (α × β × γ × δ)) (xw : α × δ) : ℝ :=
  ∑ y : β, ∑ z : γ, P.pmf (xw.1, y, z, xw.2)

def marginalYWMass (P : FinitePMF (α × β × γ × δ)) (yw : β × δ) : ℝ :=
  ∑ x : α, ∑ z : γ, P.pmf (x, yw.1, z, yw.2)

def marginalZWMass (P : FinitePMF (α × β × γ × δ)) (zw : γ × δ) : ℝ :=
  ∑ x : α, ∑ y : β, P.pmf (x, y, zw.1, zw.2)

def marginalWMass (P : FinitePMF (α × β × γ × δ)) (w : δ) : ℝ :=
  ∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z, w)

/-- Marginal of (T,A) from a PMF on (S,T,A). Used by Theorem 1. -/
def marginalTAofSTA (P : FinitePMF (α × β × γ)) (ta : β × γ) : ℝ :=
  ∑ s : α, P.pmf (s, ta.1, ta.2)

def marginalXZWMass (P : FinitePMF (α × β × γ × δ)) (xzw : α × γ × δ) : ℝ :=
  ∑ y : β, P.pmf (xzw.1, y, xzw.2.1, xzw.2.2)

def marginalYZWMass (P : FinitePMF (α × β × γ × δ)) (yzw : β × γ × δ) : ℝ :=
  ∑ x : α, P.pmf (x, yzw.1, yzw.2.1, yzw.2.2)

/-- `I(X;Z | W)` for a four-variable PMF `(X,Y,Z,W)`. -/
def I_XZ_W (P : FinitePMF (α × β × γ × δ)) : ℝ :=
  entropyOf (marginalXWMass P) +
    entropyOf (marginalZWMass P) -
    entropyOf (marginalWMass P) -
    entropyOf (marginalXZWMass P)

/-- `I(Y;Z | W)` for a four-variable PMF `(X,Y,Z,W)`. -/
def I_YZ_W (P : FinitePMF (α × β × γ × δ)) : ℝ :=
  entropyOf (marginalYWMass P) +
    entropyOf (marginalZWMass P) -
    entropyOf (marginalWMass P) -
    entropyOf (marginalYZWMass P)

/-- `H(A | T)` for a PMF on `T × A`. -/
def H_A_cond_T (Q : FinitePMF (β × γ)) : ℝ :=
  entropyOf Q.pmf - entropyOf (marginalLeftMass Q)

/-- `I(S; A | T)` for a PMF on `S × T × A`. -/
def I_SA_cond_T (P : FinitePMF (α × β × γ)) : ℝ :=
  let H_ST := entropyOf (fun (st : α × β) => ∑ a : γ, P.pmf (st.1, st.2, a))
  let H_AT := entropyOf (fun (at' : β × γ) => ∑ s : α, P.pmf (s, at'.1, at'.2))
  let H_T := entropyOf (fun (t : β) => ∑ s : α, ∑ a : γ, P.pmf (s, t, a))
  let H_STA := entropyOf P.pmf
  H_ST + H_AT - H_T - H_STA

def marginalXYWMass (P : FinitePMF (α × β × γ × δ)) (xyw : α × β × δ) : ℝ :=
  ∑ z : γ, P.pmf (xyw.1, xyw.2.1, z, xyw.2.2)

/-- `I((X,Y);Z | W)` for a four-variable PMF `(X,Y,Z,W)`. -/
def I_XY_Z_W (P : FinitePMF (α × β × γ × δ)) : ℝ :=
  entropyOf (marginalXYWMass P) +
    entropyOf (marginalZWMass P) -
    entropyOf (marginalWMass P) -
    entropyOf (fun xyzw : α × β × γ × δ => P.pmf xyzw)

/-- `I(Y;Z | X,W)` for a four-variable PMF `(X,Y,Z,W)`. -/
def I_YZ_XW (P : FinitePMF (α × β × γ × δ)) : ℝ :=
  entropyOf (marginalXYWMass P) +
    entropyOf (marginalXZWMass P) -
    entropyOf (marginalXWMass P) -
    entropyOf (fun xyzw : α × β × γ × δ => P.pmf xyzw)

/-- `I(X;Z | Y,W)` for a four-variable PMF `(X,Y,Z,W)`. -/
def I_XZ_YW (P : FinitePMF (α × β × γ × δ)) : ℝ :=
  entropyOf (marginalXYWMass P) +
    entropyOf (marginalYZWMass P) -
    entropyOf (marginalYWMass P) -
    entropyOf (fun xyzw : α × β × γ × δ => P.pmf xyzw)

lemma I_XY_Z_W_eq_I_XZ_W_add_I_YZ_XW (P : FinitePMF (α × β × γ × δ)) :
    I_XY_Z_W P = I_XZ_W P + I_YZ_XW P := by
  unfold I_XY_Z_W I_XZ_W I_YZ_XW
  ring

lemma I_XY_Z_W_eq_I_YZ_W_add_I_XZ_YW (P : FinitePMF (α × β × γ × δ)) :
    I_XY_Z_W P = I_YZ_W P + I_XZ_YW P := by
  unfold I_XY_Z_W I_YZ_W I_XZ_YW
  ring

def equivYZXW : β × γ × (α × δ) ≃ α × β × γ × δ where
  toFun t := (t.2.2.1, t.1, t.2.1, t.2.2.2)
  invFun t := (t.2.1, t.2.2.1, (t.1, t.2.2.2))
  left_inv := by
    intro t
    rcases t with ⟨y, z, x, w⟩
    rfl
  right_inv := by
    intro t
    rcases t with ⟨x, y, z, w⟩
    rfl

def equivXZYW : α × γ × (β × δ) ≃ α × β × γ × δ where
  toFun t := (t.1, t.2.2.1, t.2.1, t.2.2.2)
  invFun t := (t.1, t.2.2.1, (t.2.1, t.2.2.2))
  left_inv := by
    intro t
    rcases t with ⟨x, z, y, w⟩
    rfl
  right_inv := by
    intro t
    rcases t with ⟨x, y, z, w⟩
    rfl

def pmfYZXW (P : FinitePMF (α × β × γ × δ)) :
    FinitePMF (β × γ × (α × δ)) :=
  FinitePMF.comapEquiv equivYZXW P

def pmfXZYW (P : FinitePMF (α × β × γ × δ)) :
    FinitePMF (α × γ × (β × δ)) :=
  FinitePMF.comapEquiv equivXZYW P

lemma condMutualInfo_pmfYZXW (P : FinitePMF (α × β × γ × δ)) :
    condMutualInfo (pmfYZXW P) = I_YZ_XW P := by
  let eXYW : α × β × δ ≃ β × (α × δ) := {
    toFun := fun t => (t.2.1, (t.1, t.2.2))
    invFun := fun t => (t.2.1, t.1, t.2.2)
    left_inv := by intro t; rcases t with ⟨x, y, w⟩; rfl
    right_inv := by intro t; rcases t with ⟨y, x, w⟩; rfl
  }
  let eXZW : α × γ × δ ≃ γ × (α × δ) := {
    toFun := fun t => (t.2.1, (t.1, t.2.2))
    invFun := fun t => (t.2.1, t.1, t.2.2)
    left_inv := by intro t; rcases t with ⟨x, z, w⟩; rfl
    right_inv := by intro t; rcases t with ⟨z, x, w⟩; rfl
  }
  have hXYW : entropyOf (marginalXZMass (pmfYZXW P)) =
      entropyOf (marginalXYWMass P) := by
    symm
    refine entropyOf_equiv_eq eXYW (marginalXYWMass P)
      (marginalXZMass (pmfYZXW P)) ?_
    intro xyw
    rcases xyw with ⟨x, y, w⟩
    rfl
  have hXZW : entropyOf (marginalYZMass (pmfYZXW P)) =
      entropyOf (marginalXZWMass P) := by
    symm
    refine entropyOf_equiv_eq eXZW (marginalXZWMass P)
      (marginalYZMass (pmfYZXW P)) ?_
    intro xzw
    rcases xzw with ⟨x, z, w⟩
    rfl
  have hXW : entropyOf (marginalZMass (pmfYZXW P)) =
      entropyOf (marginalXWMass P) := by
    apply congrArg entropyOf
    funext xw
    rcases xw with ⟨x, w⟩
    rfl
  have hFull : entropyOf (fun yz_xw : β × γ × (α × δ) => (pmfYZXW P).pmf yz_xw) =
      entropyOf (fun xyzw : α × β × γ × δ => P.pmf xyzw) := by
    symm
    refine entropyOf_equiv_eq equivYZXW.symm
      (fun xyzw : α × β × γ × δ => P.pmf xyzw)
      (fun yz_xw : β × γ × (α × δ) => (pmfYZXW P).pmf yz_xw) ?_
    intro xyzw
    rcases xyzw with ⟨x, y, z, w⟩
    rfl
  unfold condMutualInfo I_YZ_XW
  rw [hXYW, hXZW, hXW, hFull]

lemma condMutualInfo_pmfXZYW (P : FinitePMF (α × β × γ × δ)) :
    condMutualInfo (pmfXZYW P) = I_XZ_YW P := by
  let eXYW : α × β × δ ≃ α × (β × δ) := {
    toFun := fun t => (t.1, (t.2.1, t.2.2))
    invFun := fun t => (t.1, t.2.1, t.2.2)
    left_inv := by intro t; rcases t with ⟨x, y, w⟩; rfl
    right_inv := by intro t; rcases t with ⟨x, y, w⟩; rfl
  }
  let eYZW : β × γ × δ ≃ γ × (β × δ) := {
    toFun := fun t => (t.2.1, (t.1, t.2.2))
    invFun := fun t => (t.2.1, t.1, t.2.2)
    left_inv := by intro t; rcases t with ⟨y, z, w⟩; rfl
    right_inv := by intro t; rcases t with ⟨z, y, w⟩; rfl
  }
  have hXYW : entropyOf (marginalXZMass (pmfXZYW P)) =
      entropyOf (marginalXYWMass P) := by
    symm
    refine entropyOf_equiv_eq eXYW (marginalXYWMass P)
      (marginalXZMass (pmfXZYW P)) ?_
    intro xyw
    rcases xyw with ⟨x, y, w⟩
    rfl
  have hYZW : entropyOf (marginalYZMass (pmfXZYW P)) =
      entropyOf (marginalYZWMass P) := by
    symm
    refine entropyOf_equiv_eq eYZW (marginalYZWMass P)
      (marginalYZMass (pmfXZYW P)) ?_
    intro yzw
    rcases yzw with ⟨y, z, w⟩
    rfl
  have hYW : entropyOf (marginalZMass (pmfXZYW P)) =
      entropyOf (marginalYWMass P) := by
    apply congrArg entropyOf
    funext yw
    rcases yw with ⟨y, w⟩
    rfl
  have hFull : entropyOf (fun xz_yw : α × γ × (β × δ) => (pmfXZYW P).pmf xz_yw) =
      entropyOf (fun xyzw : α × β × γ × δ => P.pmf xyzw) := by
    symm
    refine entropyOf_equiv_eq equivXZYW.symm
      (fun xyzw : α × β × γ × δ => P.pmf xyzw)
      (fun xz_yw : α × γ × (β × δ) => (pmfXZYW P).pmf xz_yw) ?_
    intro xyzw
    rcases xyzw with ⟨x, y, z, w⟩
    rfl
  unfold condMutualInfo I_XZ_YW
  rw [hXYW, hYZW, hYW, hFull]

/-- Conditional Markovity as a concrete definition. -/
def condMarkov (P : FinitePMF (α × β × γ × δ)) : Prop :=
  ∀ x y z w,
    P.pmf (x, y, z, w) * marginalYWMass P (y, w)
      =
    marginalXYWMass P (x, y, w) * marginalYZWMass P (y, z, w)

lemma I_YZ_XW_nonneg (P : FinitePMF (α × β × γ × δ)) :
    0 ≤ I_YZ_XW P := by
  have h := condMutualInfo_nonneg (pmfYZXW P)
  rwa [condMutualInfo_pmfYZXW P] at h

lemma I_XZ_YW_eq_zero_of_condMarkov
    (P : FinitePMF (α × β × γ × δ)) (h : condMarkov P) :
    I_XZ_YW P = 0 := by
  have hzero := condMutualInfo_eq_zero_of_condIndep (pmfXZYW P) ?_
  · rwa [condMutualInfo_pmfXZYW P] at hzero
  · intro x z yw
    rcases yw with ⟨y, w⟩
    simpa [pmfXZYW, FinitePMF.comapEquiv, equivXZYW, marginalZMass,
      marginalXZMass, marginalYZMass, marginalYWMass, marginalXYWMass,
      marginalYZWMass] using h x y z w

/-- Conditional data processing for finite PMFs. -/
theorem cond_dpi (P : FinitePMF (α × β × γ × δ)) (h : condMarkov P) :
    I_XZ_W P ≤ I_YZ_W P := by
  have hchain_x := I_XY_Z_W_eq_I_XZ_W_add_I_YZ_XW P
  have hchain_y := I_XY_Z_W_eq_I_YZ_W_add_I_XZ_YW P
  have hnonneg := I_YZ_XW_nonneg P
  have hzero := I_XZ_YW_eq_zero_of_condMarkov P h
  linarith

end

end FiniteQuerySandbox
