import Mathlib

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

/-!
# Layer 1: Finite Discrete Information Theory

Mathlib provides the finite-sum, real-logarithm, and probability infrastructure
used here. At the pinned Mathlib version, Shannon entropy and conditional mutual
information are not exported as the exact finite-discrete API needed by this
artifact, so we define those quantities locally by their standard finite PMF
formulas. The downstream chain rule, cut-set, Markov, and DPI facts remain the
only external information-theoretic axioms.
-/

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

/-- A finite discrete probability mass function over type `α`. -/
structure FinitePMF (α : Type) [Fintype α] [DecidableEq α] where
  pmf : α → ℝ
  pmf_nonneg : ∀ x, 0 ≤ pmf x
  sum_one : ∑ x : α, pmf x = 1

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

/-! ### PR 4a: Basic positivity lemmas -/

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
  rw [← Finset.sum_product]
  exact P.sum_one

lemma marginalRightMass_sum_one (P : FinitePMF (α × β)) :
    ∑ y : β, marginalRightMass P y = 1 := by
  unfold marginalRightMass
  rw [Finset.sum_comm]
  rw [← Finset.sum_product]
  exact P.sum_one

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

/-! ### PR 4b: KL nonnegativity and entropy bound -/

lemma Fintype.card_pos_of_finitePMF (P : FinitePMF α) :
    0 < Fintype.card α := by
  by_contra h
  push_neg at h
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

/-- Finite conditional entropy `H(X | Y) = H(X,Y) - H(Y)`. -/
def condEntropy (P_XY : FinitePMF (α × β)) : ℝ :=
  entropyOf (fun xy : α × β => P_XY.pmf xy) -
    entropyOf (marginalRightMass P_XY)

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

def marginalXWMass (P : FinitePMF (α × β × γ × δ)) (xw : α × δ) : ℝ :=
  ∑ y : β, ∑ z : γ, P.pmf (xw.1, y, z, xw.2)

def marginalYWMass (P : FinitePMF (α × β × γ × δ)) (yw : β × δ) : ℝ :=
  ∑ x : α, ∑ z : γ, P.pmf (x, yw.1, z, yw.2)

def marginalZWMass (P : FinitePMF (α × β × γ × δ)) (zw : γ × δ) : ℝ :=
  ∑ x : α, ∑ y : β, P.pmf (x, y, zw.1, zw.2)

def marginalWMass (P : FinitePMF (α × β × γ × δ)) (w : δ) : ℝ :=
  ∑ x : α, ∑ y : β, ∑ z : γ, P.pmf (x, y, z, w)

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

/-- Marginal of (T,A) from a PMF on (S,T,A). Used by Theorem 1. -/
def marginalTAofSTA (P : FinitePMF (α × β × γ)) (ta : β × γ) : ℝ :=
  ∑ s : α, P.pmf (s, ta.1, ta.2)

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

/-- Conditional Markovity as a concrete definition. -/
def condMarkov (P : FinitePMF (α × β × γ × δ)) : Prop :=
  ∀ x y z w,
    P.pmf (x, y, z, w) * marginalYWMass P (y, w)
      =
    marginalXYWMass P (x, y, w) * marginalYZWMass P (y, z, w)

/-- Conditional data processing remains an explicit external axiom. -/
axiom cond_dpi (P : FinitePMF (α × β × γ × δ)) (h : condMarkov P) :
    I_XZ_W P ≤ I_YZ_W P

end

end FiniteQuerySandbox
