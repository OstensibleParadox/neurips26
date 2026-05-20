import FiniteQuerySandbox.InfoTheory.Conditional

open Finset
open scoped BigOperators Real

namespace FiniteQuerySandbox

noncomputable section

variable {α β γ δ : Type} [Fintype α] [Fintype β] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β] [DecidableEq γ] [DecidableEq δ]

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
