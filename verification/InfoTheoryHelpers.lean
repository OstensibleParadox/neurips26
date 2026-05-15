import Mathlib
import .CutSetBoundExtract

open Finset
open scoped BigOperators Real

namespace InfoTheory

open CutSetBoundExtract

-- ============================================================
-- Generic marginal definitions for arbitrary finite product types
-- ============================================================

section Marginals

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

/-- Marginal of A from P(A, B, C). -/
def marginalA (P : FinitePMF (α × β × γ)) (a : α) : ℝ :=
  ∑ b : β, ∑ c : γ, P.pmf (a, b, c)

/-- Marginal of B from P(A, B, C). -/
def marginalB (P : FinitePMF (α × β × γ)) (b : β) : ℝ :=
  ∑ a : α, ∑ c : γ, P.pmf (a, b, c)

/-- Marginal of C from P(A, B, C). -/
def marginalC (P : FinitePMF (α × β × γ)) (c : γ) : ℝ :=
  ∑ a : α, ∑ b : β, P.pmf (a, b, c)

/-- Joint marginal (A, B) from P(A, B, C). -/
def marginalAB (P : FinitePMF (α × β × γ)) (ab : α × β) : ℝ :=
  ∑ c : γ, P.pmf (ab.1, ab.2, c)

/-- Joint marginal (A, C) from P(A, B, C). -/
def marginalAC (P : FinitePMF (α × β × γ)) (ac : α × γ) : ℝ :=
  ∑ b : β, P.pmf (ac.1, b, ac.2)

/-- Joint marginal (B, C) from P(A, B, C). -/
def marginalBC (P : FinitePMF (α × β × γ)) (bc : β × γ) : ℝ :=
  ∑ a : α, P.pmf (a, bc.1, bc.2)

end Marginals

-- ============================================================
-- Mutual information definitions over a triple P(A, B, C)
-- ============================================================

section MutualInfo

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

/-- I(A; B) = H(A) + H(B) - H(A, B). -/
def I_AB (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalA P) + entropyOf (marginalB P) - entropyOf (marginalAB P)

/-- I(A; C) = H(A) + H(C) - H(A, C). -/
def I_AC (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalA P) + entropyOf (marginalC P) - entropyOf (marginalAC P)

/-- I(A; B, C) = H(A) + H(B, C) - H(A, B, C).
    Mutual info between A and the joint variable (B, C). -/
def I_A_BC (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalA P) + entropyOf (marginalBC P) - entropy P

/-- I(A; C | B) = H(A, B) + H(B, C) - H(B) - H(A, B, C).
    Conditional mutual info between A and C given B. -/
def I_A_cond_C_B (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalAB P) + entropyOf (marginalBC P) -
    entropyOf (marginalB P) - entropy P

/-- I(A; B | C) = H(A, C) + H(B, C) - H(C) - H(A, B, C).
    Conditional mutual info between A and B given C. -/
def I_A_cond_B_C (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalAC P) + entropyOf (marginalBC P) -
    entropyOf (marginalC P) - entropy P

end MutualInfo

-- ============================================================
-- Basic entropy non-negativity (Lemma 1)
-- ============================================================

lemma pmf_le_one {α : Type} [Fintype α] [DecidableEq α] (P : FinitePMF α) (x : α) :
    P.pmf x ≤ 1 := by
  have h_nonneg : ∀ y : α, 0 ≤ P.pmf y := P.pmf_nonneg
  have : P.pmf x ≤ ∑ y : α, P.pmf y :=
    Finset.single_le_sum (fun y _ => h_nonneg y) (Finset.mem_univ x)
  linarith [P.sum_one]

lemma negMulLog2_nonneg_lemma {p : ℝ} (hp0 : 0 ≤ p) (hp1 : p ≤ 1) : 0 ≤ negMulLog2 p := by
  unfold negMulLog2
  by_cases hz : p = 0
  · simp [hz]
  · have hp_pos : 0 < p := lt_of_le_of_ne hp0 (Ne.symm hz)
    have hlog_le : Real.log p ≤ 0 :=
      (Real.log_le_sub_one_of_pos hp_pos).trans (by linarith : p - 1 ≤ 0)
    have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
    have h_div_le : Real.log p / Real.log 2 ≤ 0 :=
      div_nonpos_of_nonpos_of_nonneg hlog_le hlog2_pos.le
    have h_prod_le : p * (Real.log p / Real.log 2) ≤ 0 :=
      mul_nonpos_of_nonneg_of_nonpos hp0 h_div_le
    linarith

lemma entropy_nonneg {α : Type} [Fintype α] [DecidableEq α] (P : FinitePMF α) :
    0 ≤ entropy P := by
  unfold entropy entropyOf
  refine Finset.sum_nonneg (fun x _ => ?_)
  exact negMulLog2_nonneg_lemma (P.pmf_nonneg x) (pmf_le_one P x)

-- ============================================================
-- entropyOf_mul_log2: convert entropy sum to -Σ p·log(p)
-- ============================================================

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
    _ = -∑ x : η, mass x * Real.log (mass x) := by rw [Finset.sum_neg_distrib]

-- ============================================================
-- Marginal pull-through lemma:
--   Σ_{a,b} P(a,b) * f(a,b) = Σ_{a,b,c} P(a,b,c) * f(a,b)
-- ============================================================

lemma marginalAB_pullback (P : FinitePMF (α × β × γ)) (f : α × β → ℝ) :
    ∑ (ab : α × β), marginalAB P ab * f ab =
    ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * f (a, b) := by
  unfold marginalAB
  simp_rw [Finset.sum_prod_type]
  calc
    ∑ a : α, ∑ b : β, (∑ c : γ, P.pmf (a, b, c)) * f (a, b)
        = ∑ a : α, ∑ b : β, ∑ c : γ, P.pmf (a, b, c) * f (a, b) := by
          refine Finset.sum_congr rfl (fun a _ => Finset.sum_congr rfl (fun b _ => ?_))
          rw [Finset.mul_sum]
    _ = ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * f (a, b) := rfl

lemma marginalBC_pullback (P : FinitePMF (α × β × γ)) (f : β × γ → ℝ) :
    ∑ (bc : β × γ), marginalBC P bc * f bc =
    ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * f (b, c) := by
  unfold marginalBC
  simp_rw [Finset.sum_prod_type]
  calc
    ∑ b : β, ∑ c : γ, (∑ a : α, P.pmf (a, b, c)) * f (b, c)
        = ∑ b : β, ∑ c : γ, ∑ a : α, P.pmf (a, b, c) * f (b, c) := by
          refine Finset.sum_congr rfl (fun b _ => Finset.sum_congr rfl (fun c _ => ?_))
          rw [Finset.mul_sum]
    _ = ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * f (b, c) := by
      simp_rw [Finset.sum_comm]

lemma marginalB_pullback (P : FinitePMF (α × β × γ)) (f : β → ℝ) :
    ∑ (b : β), marginalB P b * f b =
    ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * f b := by
  unfold marginalB
  simp_rw [Finset.sum_prod_type]
  calc
    ∑ b : β, (∑ a : α, ∑ c : γ, P.pmf (a, b, c)) * f b
        = ∑ b : β, ∑ a : α, ∑ c : γ, P.pmf (a, b, c) * f b := by
          refine Finset.sum_congr rfl (fun b _ => ?_)
          simp_rw [Finset.sum_mul, Finset.sum_product]
    _ = ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * f b := by
      simp_rw [Finset.sum_comm]

-- ============================================================
-- Chain Rule 1: I(A; B, C) = I(A; B) + I(A; C | B)
-- ============================================================

lemma chain_rule_I_A_BC (P : FinitePMF (α × β × γ)) :
    I_A_BC P = I_AB P + I_A_cond_C_B P := by
  unfold I_A_BC I_AB I_A_cond_C_B
  unfold marginalA marginalB marginalAB marginalBC
  ring

-- ============================================================
-- Chain Rule 2: I(A; B, C) = I(A; C) + I(A; B | C)
-- ============================================================

lemma chain_rule_I_A_BC_alt (P : FinitePMF (α × β × γ)) :
    I_A_BC P = I_AC P + I_A_cond_B_C P := by
  unfold I_A_BC I_AC I_A_cond_B_C
  unfold marginalA marginalC marginalAC marginalBC
  ring

-- ============================================================
-- Lemma 2: Mutual information chain rule
--   I(A, B; C) = I(A; C) + I(B; C | A)
-- (Using the definition from CutSetBoundExtract's target pattern)
-- ============================================================

/-- I(B; C | A) = H(A, B) + H(A, C) - H(A) - H(A, B, C).
    Defined symmetrically to the existing I_S_M_cond_Ttilde pattern. -/
def I_BC_cond_A (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalAB P) + entropyOf (marginalAC P) -
    entropyOf (marginalA P) - entropy P

/-- I(A, B; C) = H(A, C) + H(B, C) - H(C) - H(A, B, C).
    Joint mutual info between (A, B) and C. -/
def I_AB_C (P : FinitePMF (α × β × γ)) : ℝ :=
  entropyOf (marginalAC P) + entropyOf (marginalBC P) -
    entropyOf (marginalC P) - entropy P

lemma mutual_info_chain_rule {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
    [DecidableEq α] [DecidableEq β] [DecidableEq γ]
    (P : FinitePMF (α × β × γ)) :
    I_AB_C P = I_AC P + I_BC_cond_A P := by
  unfold I_AB_C I_AC I_BC_cond_A
  unfold marginalAC marginalBC marginalC marginalAB marginalA
  ring

-- ============================================================
-- Lemma 3: Data Processing Inequality (DPI)
--   If A → B → C are Markov, then I(A; C) ≤ I(A; B)
-- ============================================================

section DPI

variable {α β γ : Type} [Fintype α] [Fintype β] [Fintype γ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ]

/--
Markov chain condition A → B → C.
Equivalently: A and C are conditionally independent given B:
  P(a, b, c) * P(b) = P(a, b) * P(b, c)   ∀ a, b, c
where P(b) = ∑_{a,c} P(a,b,c), P(a,b) = ∑_c P(a,b,c), P(b,c) = ∑_a P(a,b,c).
-/
def IsMarkovChain (P : FinitePMF (α × β × γ)) : Prop :=
  ∀ a b c,
    P.pmf (a, b, c) * marginalB P b = marginalAB P (a, b) * marginalBC P (b, c)

/--
I(A; C | B) = 0 under Markov chain A → B → C.

Expanding into log-sum form:
  I(A; C | B) = Σ_{a,b,c} P(a,b,c) * log₂(P(a,b,c) * P(b) / (P(a,b) * P(b,c)))

Under the Markov condition IsMarkovChain P, the ratio inside the log is 1 for all
(a,b,c) where the denominator is positive, and log(1) = 0.  For terms where the
denominator is zero, the Markov condition forces the numerator to be zero, and by the
convention 0*log(0/0) = 0, the term vanishes.

Proof using entropy expansions:
  I(A; C | B) = H(A,B) + H(B,C) - H(B) - H(A,B,C)
  Pull each entropy through the marginal sums:
    H(A,B) = -Σ P(a,b,c) * log₂(P(a,b))
    H(B,C) = -Σ P(a,b,c) * log₂(P(b,c))
    H(B)   = -Σ P(a,b,c) * log₂(P(b))
    H(A,B,C) = -Σ P(a,b,c) * log₂(P(a,b,c))
  Combining:
    I(A; C | B) = Σ P(a,b,c) * log₂(P(a,b,c) * P(b) / (P(a,b) * P(b,c)))
  The Markov condition makes the ratio 1, so log₂(1) = 0 and the sum is 0.

NOTE: The pullback from marginal sums to the triple sum is proved by the
marginal_pullback lemmas above.  The remaining step of recognizing that the
ratio is 1 under hMC requires case-splitting on zero denominators and applying
hMC, which is an algebraic identity on the real PMF values.
-/
lemma cond_mutual_info_zero_of_markov (P : FinitePMF (α × β × γ))
    (hMC : IsMarkovChain P) :
    I_A_cond_C_B P = 0 := by
  unfold I_A_cond_C_B
  -- Write each entropy in log-sum form, then pull back to the triple sum.
  have hlog2_ne_zero : Real.log 2 ≠ 0 := by positivity
  -- We show I(A; C | B) * log(2) = 0 using the marginal pullback lemmas.
  -- Expand: I(A; C | B) = H(A,B) + H(B,C) - H(B) - P
  -- Using entropyOf_mul_log2 to convert to -Σ P * log P form:
  have h_entropy_mul_log2 : I_A_cond_C_B P * Real.log 2 =
      -(∑ (ab : α × β), marginalAB P ab * Real.log (marginalAB P ab))
      -(∑ (bc : β × γ), marginalBC P bc * Real.log (marginalBC P bc))
      +(∑ (b : β), marginalB P b * Real.log (marginalB P b))
      +(∑ (abc : α × β × γ), P.pmf abc * Real.log (P.pmf abc)) := by
    unfold I_A_cond_C_B
    have hAB := entropyOf_mul_log2 (marginalAB P)
    have hBC := entropyOf_mul_log2 (marginalBC P)
    have hB  := entropyOf_mul_log2 (marginalB P)
    have hP  := entropyOf_mul_log2 (P.pmf)
    have hsum : (entropyOf (marginalAB P) + entropyOf (marginalBC P) -
      entropyOf (marginalB P) - entropy P) * Real.log 2 =
      (entropyOf (marginalAB P) * Real.log 2) +
      (entropyOf (marginalBC P) * Real.log 2) -
      (entropyOf (marginalB P) * Real.log 2) -
      (entropy P * Real.log 2) := by ring
    rw [hsum, hAB, hBC, hB, hP]
    ring
  -- Pull each marginal sum back to the triple sum:
  have h_pull_AB : ∑ (ab : α × β), marginalAB P ab * Real.log (marginalAB P ab) =
      ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * Real.log (marginalAB P (a, b)) := by
    simpa using marginalAB_pullback P (fun ab => Real.log (marginalAB P ab))
  have h_pull_BC : ∑ (bc : β × γ), marginalBC P bc * Real.log (marginalBC P bc) =
      ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * Real.log (marginalBC P (b, c)) := by
    simpa using marginalBC_pullback P (fun bc => Real.log (marginalBC P bc))
  have h_pull_B : ∑ (b : β), marginalB P b * Real.log (marginalB P b) =
      ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * Real.log (marginalB P b) := by
    simpa using marginalB_pullback P (fun b => Real.log (marginalB P b))
  have h_pull_P : ∑ (abc : α × β × γ), P.pmf abc * Real.log (P.pmf abc) =
      ∑ (a : α) (b : β) (c : γ), P.pmf (a, b, c) * Real.log (P.pmf (a, b, c)) := by
    simp [Finset.sum_prod_type]
  -- Substitute all four pullbacks into h_entropy_mul_log2, combining into a single triple sum:
  rw [h_pull_AB, h_pull_BC, h_pull_B, h_pull_P] at h_entropy_mul_log2
  -- Now h_entropy_mul_log2 says:
  --   I * log(2) = Σ_{a,b,c} P(a,b,c) * [log(P(a,b,c)) + log(P(b)) - log(P(a,b)) - log(P(b,c))]
  -- We show each summand is 0 under the Markov condition.
  have h_term_zero : ∀ (a : α) (b : β) (c : γ),
      P.pmf (a, b, c) * (Real.log (P.pmf (a, b, c)) + Real.log (marginalB P b)
      - Real.log (marginalAB P (a, b)) - Real.log (marginalBC P (b, c))) = 0 := by
    intro a b c
    by_cases hx : P.pmf (a, b, c) = 0
    · simp [hx]
    · have hp_pos : 0 < P.pmf (a, b, c) := lt_of_le_of_ne (P.pmf_nonneg _) (Ne.symm hx)
      -- From positivity of P(a,b,c), all relevant marginals are also > 0
      have hAB_pos : 0 < marginalAB P (a, b) := by
        unfold marginalAB
        have : P.pmf (a, b, c) ≤ ∑ (c' : γ), P.pmf (a, b, c') :=
          Finset.single_le_sum (fun c' _ => P.pmf_nonneg (a, b, c')) (Finset.mem_univ c)
        exact lt_of_lt_of_le hp_pos this
      have hBC_pos : 0 < marginalBC P (b, c) := by
        unfold marginalBC
        have : P.pmf (a, b, c) ≤ ∑ (a' : α), P.pmf (a', b, c) :=
          Finset.single_le_sum (fun a' _ => P.pmf_nonneg (a', b, c)) (Finset.mem_univ a)
        exact lt_of_lt_of_le hp_pos this
      have hB_pos : 0 < marginalB P b := by
        unfold marginalB
        have h_single : P.pmf (a, b, c) ≤ ∑ (a' : α), ∑ (c' : γ), P.pmf (a', b, c') :=
          calc
            P.pmf (a, b, c) ≤ ∑ (c' : γ), P.pmf (a, b, c') :=
              Finset.single_le_sum (fun c' _ => P.pmf_nonneg (a, b, c')) (Finset.mem_univ c)
            _ ≤ ∑ (a' : α), ∑ (c' : γ), P.pmf (a', b, c') :=
              Finset.single_le_sum (fun a' _ =>
                Finset.sum_nonneg (fun c' _ => P.pmf_nonneg (a', b, c'))) (Finset.mem_univ a)
        exact lt_of_lt_of_le hp_pos h_single
      have hMC_eq := hMC a b c
      -- hMC_eq: P(a,b,c) * marginalB b = marginalAB (a,b) * marginalBC (b,c)
      -- Apply log to both sides: log(xy) = log(zw) → log x + log y = log z + log w
      have h_log_eq : Real.log (P.pmf (a, b, c)) + Real.log (marginalB P b) =
          Real.log (marginalAB P (a, b)) + Real.log (marginalBC P (b, c)) := by
        calc
          Real.log (P.pmf (a, b, c)) + Real.log (marginalB P b) =
              Real.log ((P.pmf (a, b, c)) * (marginalB P b)) := by
            rw [Real.log_mul (ne_of_gt hp_pos) (ne_of_gt hB_pos)]
          _ = Real.log ((marginalAB P (a, b)) * (marginalBC P (b, c))) := by rw [hMC_eq]
          _ = Real.log (marginalAB P (a, b)) + Real.log (marginalBC P (b, c)) := by
            rw [Real.log_mul (ne_of_gt hAB_pos) (ne_of_gt hBC_pos)]
      -- The inner expression simplifies to 0
      have h_inner_zero : Real.log (P.pmf (a, b, c)) + Real.log (marginalB P b)
          - Real.log (marginalAB P (a, b)) - Real.log (marginalBC P (b, c)) = 0 := by
        linarith [h_log_eq]
      -- So the product is P(a,b,c) * 0 = 0
      simp [h_inner_zero]
  -- Summing the zero terms gives zero, so I(A; C | B) * log(2) = 0
  have h_sum_zero : ∑ (a : α) (b : β) (c : γ),
      P.pmf (a, b, c) * (Real.log (P.pmf (a, b, c)) + Real.log (marginalB P b)
      - Real.log (marginalAB P (a, b)) - Real.log (marginalBC P (b, c))) = 0 := by
    simp [h_term_zero]
  rw [h_sum_zero] at h_entropy_mul_log2
  -- Now: I_A_cond_C_B P * Real.log 2 = 0
  -- Since Real.log 2 > 0, we conclude I_A_cond_C_B P = 0
  have hlog2_pos : 0 < Real.log 2 := Real.log_pos (by norm_num : (1 : ℝ) < 2)
  have hlog2_ne_zero : Real.log 2 ≠ 0 := by linarith
  rcases mul_eq_zero.mp h_entropy_mul_log2 with (h | h)
  · exact h
  · exfalso; exact hlog2_ne_zero h

/--
Non-negativity of conditional mutual information I(A; B | C) ≥ 0.

This is a standard information-theoretic fact: conditioning reduces entropy.
  I(A; B | C) = H(A, C) + H(B, C) - H(C) - H(A, B, C) ≥ 0

The proof follows from the log-sum inequality (convexity of t ↦ t·log t):
  Σ_{a,b,c} P(a,b,c) * log(P(a,b,c) * P(c) / (P(a,c) * P(b,c))) ≥ 0
which equals I(A; B | C) after expansion.

For the finite-discrete case, this is equivalent to subadditivity of joint entropy:
  H(A, C) + H(B, C) ≥ H(C) + H(A, B, C)

In the dual-certificate Lean artifact (FiniteQuerySandbox), this fact is assumed
as a basic property of the information-theoretic quantities.  A rigorous proof
would require establishing the log-sum inequality via Jensen's inequality for
the convex function φ(t) = t·log₂(t).
-/
lemma I_A_cond_B_C_nonneg (P : FinitePMF (α × β × γ)) :
    0 ≤ I_A_cond_B_C P := by
  have h_eq : I_A_cond_B_C P = FiniteQuerySandbox.condMutualInfo P := by
    unfold I_A_cond_B_C FiniteQuerySandbox.condMutualInfo
    unfold marginalAC marginalBC marginalC
    unfold FiniteQuerySandbox.marginalXZMass FiniteQuerySandbox.marginalYZMass FiniteQuerySandbox.marginalZMass
    simp
  rw [h_eq]
  exact FiniteQuerySandbox.condMutualInfo_nonneg P

/--
Data Processing Inequality:
If A → B → C form a Markov chain, then I(A; C) ≤ I(A; B).

Proof:
  1. Chain rule: I(A; B, C) = I(A; B) + I(A; C | B)  (chain_rule_I_A_BC)
  2. Chain rule: I(A; B, C) = I(A; C) + I(A; B | C)  (chain_rule_I_A_BC_alt)
  3. From (1) and (2): I(A; B) + I(A; C | B) = I(A; C) + I(A; B | C)
  4. Under Markov A → B → C: I(A; C | B) = 0  (cond_mutual_info_zero_of_markov)
     So I(A; B) = I(A; C) + I(A; B | C)
  5. By non-negativity: I(A; B | C) ≥ 0  (I_A_cond_B_C_nonneg)
     Therefore I(A; B) ≥ I(A; C).
-/
lemma data_processing_inequality (P : FinitePMF (α × β × γ))
    (hMC : IsMarkovChain P) :
    I_AC P ≤ I_AB P := by
  have h_chain1 := chain_rule_I_A_BC P
  have h_chain2 := chain_rule_I_A_BC_alt P
  have h_cond_zero : I_A_cond_C_B P = 0 := cond_mutual_info_zero_of_markov P hMC
  have h_nonneg_cond : 0 ≤ I_A_cond_B_C P := I_A_cond_B_C_nonneg P
  -- From h_chain1 and h_chain2:
  -- I_AB P + I_A_cond_C_B P = I_AC P + I_A_cond_B_C P
  have h_eq : I_AB P + I_A_cond_C_B P = I_AC P + I_A_cond_B_C P := by
    calc
      I_AB P + I_A_cond_C_B P = I_A_BC P := by symm; exact h_chain1
      _ = I_AC P + I_A_cond_B_C P := h_chain2
  rw [h_cond_zero] at h_eq
  -- Now: I_AB P = I_AC P + I_A_cond_B_C P
  -- So I_AB P - I_AC P = I_A_cond_B_C P ≥ 0
  linarith

end DPI
