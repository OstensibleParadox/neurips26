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

def marginalLeftMass (P : FinitePMF (α × β)) (x : α) : ℝ :=
  ∑ y : β, P.pmf (x, y)

def marginalRightMass (P : FinitePMF (α × β)) (y : β) : ℝ :=
  ∑ x : α, P.pmf (x, y)

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
