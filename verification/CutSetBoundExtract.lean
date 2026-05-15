import Mathlib
import FiniteQuerySandbox.InfoTheory
import FiniteQuerySandbox.DualCertificate

namespace FiniteQuerySandbox

open Finset
open scoped BigOperators Real

noncomputable section

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

/--
定义通用分布推向 (Pushforward)。
给定 P : FinitePMF α 和函数 f : α → β，构造在 β 上的分布。
质量守恒由 Finset.sum_comm 保证。
-/
def FinitePMF.map
    {α β : Type} [Fintype α] [DecidableEq α] [Fintype β] [DecidableEq β]
    (P : FinitePMF α) (f : α → β) : FinitePMF β where
  pmf y := ∑ x : α, if f x = y then P.pmf x else 0
  pmf_nonneg y := by
    apply Finset.sum_nonneg
    intro x _
    by_cases h : f x = y
    · simp [h, P.pmf_nonneg x]
    · simp [h]
  sum_one := by
    calc
      ∑ y : β, ∑ x : α, (if f x = y then P.pmf x else 0)
          = ∑ x : α, ∑ y : β, (if f x = y then P.pmf x else 0) := by
            exact Finset.sum_comm
      _ = ∑ x : α, P.pmf x := by
        apply Finset.sum_congr rfl
        intro x _
        calc
          ∑ y : β, (if f x = y then P.pmf x else 0)
              = P.pmf x * ∑ y : β, (if f x = y then (1 : ℝ) else 0) := by
                  rw [Finset.mul_sum]
                  apply Finset.sum_congr rfl
                  intro y _
                  by_cases h : f x = y
                  · simp [h]
                  · simp [h]
          _ = P.pmf x := by simp
      _ = 1 := P.sum_one

/--
具体化推向：从 (S, T, M) 映射到 (S, Cut, M, T)。
变量对应关系：X=S, Y=Cut, Z=M, W=T。
-/
def pmf_from_vars {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) :
    FinitePMF (State × CutVars × MissingTrace × VisibleTrace) :=
  FinitePMF.map P (fun stm => (stm.1, Ω_vars stm, stm.2.2, stm.2.1))

lemma pmf_from_vars_apply {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars)
    (s : State) (k : CutVars) (m : MissingTrace) (t : VisibleTrace) :
    (pmf_from_vars P Ω_vars).pmf (s, k, m, t) =
      if Ω_vars (s, t, m) = k then P.pmf (s, t, m) else 0 := by
  change
    (∑ x : State × VisibleTrace × MissingTrace,
      if (x.1, Ω_vars x, x.2.2, x.2.1) = (s, k, m, t) then P.pmf x else 0)
      =
        if Ω_vars (s, t, m) = k then P.pmf (s, t, m) else 0
  by_cases h : Ω_vars (s, t, m) = k
  · rw [if_pos h]
    rw [Finset.sum_eq_single (s, t, m)]
    · simp [h]
    · intro x _ hx
      simp only [ite_eq_right_iff]
      intro hcond
      exfalso
      apply hx
      rcases Prod.ext_iff.mp hcond with ⟨hs, rest⟩
      rcases Prod.ext_iff.mp rest with ⟨_, rest2⟩
      rcases Prod.ext_iff.mp rest2 with ⟨hm, ht⟩
      ext
      · exact hs
      · exact ht
      · exact hm
    · intro hmem
      simp at hmem
  · rw [if_neg h]
    apply Finset.sum_eq_zero
    intro x _
    simp only [ite_eq_right_iff]
    intro hcond
    exfalso
    apply h
    rcases Prod.ext_iff.mp hcond with ⟨hs, rest⟩
    rcases Prod.ext_iff.mp rest with ⟨hΩ, rest2⟩
    rcases Prod.ext_iff.mp rest2 with ⟨hm, ht⟩
    have hx : x = (s, t, m) := by
      ext
      · exact hs
      · exact ht
      · exact hm
    simpa [hx] using hΩ

/-! ### 等价性层：证明边缘分布对应关系 -/

lemma marginalXWMass_eq_stateVisibleMass {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) (st : State × VisibleTrace) :
    marginalXWMass (pmf_from_vars P Ω_vars) (st.1, st.2) = stateVisibleMass P st := by
  unfold marginalXWMass stateVisibleMass
  calc
    ∑ k : CutVars, ∑ m : MissingTrace, (pmf_from_vars P Ω_vars).pmf (st.1, k, m, st.2)
        =
      ∑ k : CutVars, ∑ m : MissingTrace,
        if Ω_vars (st.1, st.2, m) = k then P.pmf (st.1, st.2, m) else 0 := by
          simp [pmf_from_vars_apply]
    _ =
      ∑ m : MissingTrace, ∑ k : CutVars,
        if Ω_vars (st.1, st.2, m) = k then P.pmf (st.1, st.2, m) else 0 := by
          rw [Finset.sum_comm]
    _ = ∑ m : MissingTrace, P.pmf (st.1, st.2, m) := by
          simp

lemma marginalWMass_eq_visibleMass {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) (t : VisibleTrace) :
    marginalWMass (pmf_from_vars P Ω_vars) t = visibleMass P t := by
  unfold marginalWMass visibleMass
  calc
    ∑ s : State, ∑ k : CutVars, ∑ m : MissingTrace,
        (pmf_from_vars P Ω_vars).pmf (s, k, m, t)
        =
      ∑ s : State, ∑ k : CutVars, ∑ m : MissingTrace,
        if Ω_vars (s, t, m) = k then P.pmf (s, t, m) else 0 := by
          simp [pmf_from_vars_apply]
    _ =
      ∑ s : State, ∑ m : MissingTrace, ∑ k : CutVars,
        if Ω_vars (s, t, m) = k then P.pmf (s, t, m) else 0 := by
          apply Finset.sum_congr rfl
          intro s _
          rw [Finset.sum_comm]
    _ = ∑ s : State, ∑ m : MissingTrace, P.pmf (s, t, m) := by
          simp

lemma marginalZWMass_eq_visibleMissingMass_swap {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) (mt : MissingTrace × VisibleTrace) :
    marginalZWMass (pmf_from_vars P Ω_vars) mt = visibleMissingMass P (mt.2, mt.1) := by
  unfold marginalZWMass visibleMissingMass
  change
    (∑ s : State, ∑ k : CutVars, (pmf_from_vars P Ω_vars).pmf (s, k, mt.1, mt.2))
      =
        ∑ s : State, P.pmf (s, mt.2, mt.1)
  calc
    ∑ s : State, ∑ k : CutVars, (pmf_from_vars P Ω_vars).pmf (s, k, mt.1, mt.2)
        =
      ∑ s : State, ∑ k : CutVars,
        if Ω_vars (s, mt.2, mt.1) = k then P.pmf (s, mt.2, mt.1) else 0 := by
          apply Finset.sum_congr rfl
          intro s _
          apply Finset.sum_congr rfl
          intro k _
          simpa using pmf_from_vars_apply P Ω_vars s k mt.1 mt.2
    _ = ∑ s : State, P.pmf (s, mt.2, mt.1) := by
          simp

lemma marginalXZWMass_eq_P_swap {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) (smt : State × MissingTrace × VisibleTrace) :
    marginalXZWMass (pmf_from_vars P Ω_vars) smt = P.pmf (smt.1, smt.2.2, smt.2.1) := by
  unfold marginalXZWMass
  change
    (∑ k : CutVars, (pmf_from_vars P Ω_vars).pmf (smt.1, k, smt.2.1, smt.2.2))
      =
        P.pmf (smt.1, smt.2.2, smt.2.1)
  calc
    ∑ k : CutVars, (pmf_from_vars P Ω_vars).pmf (smt.1, k, smt.2.1, smt.2.2)
        =
      ∑ k : CutVars,
        if Ω_vars (smt.1, smt.2.2, smt.2.1) = k
          then P.pmf (smt.1, smt.2.2, smt.2.1)
          else 0 := by
          apply Finset.sum_congr rfl
          intro k _
          simpa using pmf_from_vars_apply P Ω_vars smt.1 k smt.2.1 smt.2.2
    _ = P.pmf (smt.1, smt.2.2, smt.2.1) := by
          simp

/-- 
核心等价性：原始互信息等于推向后的四变量互信息。
证明思路：将 CMI 拆解为四个熵项，分别利用边缘等价性和熵的置换不变性证明相等。
-/
lemma I_original_eq_I_XZ_W_pmf_from_vars {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) :
    I_S_M_cond_Ttilde P = I_XZ_W (pmf_from_vars P Ω_vars) := by
  let P4 := pmf_from_vars P Ω_vars
  
  have hXW : entropyOf (marginalXWMass P4) = entropyOf (stateVisibleMass P) := by
    unfold entropyOf
    apply sum_congr rfl
    intro xw _
    rw [marginalXWMass_eq_stateVisibleMass]

  have hZW : entropyOf (marginalZWMass P4) = entropyOf (visibleMissingMass P) := by
    let e : (MissingTrace × VisibleTrace) ≃ (VisibleTrace × MissingTrace) := Equiv.prodComm MissingTrace VisibleTrace
    exact entropyOf_equiv_eq e (fun mt => marginalZWMass P4 mt) (visibleMissingMass P)
      (fun mt => by simpa using marginalZWMass_eq_visibleMissingMass_swap P Ω_vars mt)

  have hW : entropyOf (marginalWMass P4) = entropyOf (visibleMass P) := by
    unfold entropyOf
    apply sum_congr rfl
    intro w _
    rw [marginalWMass_eq_visibleMass]

  have hXZW : entropyOf (marginalXZWMass P4) = fullTraceEntropy P := by
    let e : (State × MissingTrace × VisibleTrace) ≃ (State × VisibleTrace × MissingTrace) := 
      (Equiv.refl State).prodCongr (Equiv.prodComm MissingTrace VisibleTrace)
    unfold fullTraceEntropy
    exact entropyOf_equiv_eq e (fun smt => marginalXZWMass P4 smt) P.pmf
      (fun smt => by simpa using marginalXZWMass_eq_P_swap P Ω_vars smt)

  unfold I_S_M_cond_Ttilde I_XZ_W
  rw [hXW, hZW, hW, hXZW]

/-! ### 推理层：分层证明 Cut-Set Bound -/

/--
DPI 瓶颈定理：由条件马尔可夫性推出的信息流限制。
I(S; M | T_tilde) ≤ I(Cut; M | T_tilde)
-/
theorem cut_set_dpi_bound {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars)
    (h_markov : condMarkov (pmf_from_vars P Ω_vars)) :
    I_S_M_cond_Ttilde P ≤ I_YZ_W (pmf_from_vars P Ω_vars) := by
  let P4 := pmf_from_vars P Ω_vars
  have h_eq : I_S_M_cond_Ttilde P = I_XZ_W P4 := 
    I_original_eq_I_XZ_W_pmf_from_vars P Ω_vars
  have h_dpi : I_XZ_W P4 ≤ I_YZ_W P4 := 
    cond_dpi P4 h_markov
  calc
    I_S_M_cond_Ttilde P = I_XZ_W P4 := h_eq
    _ ≤ I_YZ_W P4 := h_dpi

/--
抽象 Cut-Set Bound 定理。
连接拓扑瓶颈 (DPI) 与具体的容量上界 (h_cap)。
-/
theorem abstract_cut_set_bound
    {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars)
    (C_cut_Ω : ℝ)
    (h_markov : condMarkov (pmf_from_vars P Ω_vars))
    (h_cap : I_YZ_W (pmf_from_vars P Ω_vars) ≤ C_cut_Ω) :
    I_S_M_cond_Ttilde P ≤ C_cut_Ω := by
  exact le_trans (cut_set_dpi_bound P Ω_vars h_markov) h_cap

/--
从切集前提出发推导状态熵的上界。
这是连接拓扑分析与最终安全结论的便捷入口。
-/
theorem prop1_static_ub_from_cut
    {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars)
    (C_cut_Ω : ℝ)
    (h_markov : condMarkov (pmf_from_vars P Ω_vars))
    (h_cap : I_YZ_W (pmf_from_vars P Ω_vars) ≤ C_cut_Ω) :
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_cut_Ω := by
  -- 使用 DualCertificate.lean 中的 prop1_static_ub
  apply prop1_static_ub Unit (fun _ => C_cut_Ω) () P
  exact abstract_cut_set_bound P Ω_vars C_cut_Ω h_markov h_cap

end

end FiniteQuerySandbox
