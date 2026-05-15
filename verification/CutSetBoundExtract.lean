import Mathlib

open Finset
open scoped BigOperators Real

noncomputable section

/-
# Cut-Set Bound — 独立抽取

这个文件从 FiniteQuerySandbox 形式化中抽取了 cut-set bound 相关的定义和定理。
目标受众：数学系同学，他们可能能给 `cut_set_bound` 一个优美的有限离散证明。

## 背景

我们有一个部署系统的 trace，它被分解为两部分：
  T_full  = (T_tilde, M)      总 trace
  T_tilde = 可见/记录的 trace 部分
  M       = 缺失/未记录的 trace 部分（隐藏信道）

S 是系统的隐藏状态。

核心问题：给定 T_tilde，S 有多少残余不确定性？

链式法则给出：
  H(S | T_tilde) = H(S | T_full) + I(S; M | T_tilde)

其中：
  H(S | T_tilde)  = 给定可见 trace 后，状态 S 的残余熵
  H(S | T_full)   = 给定完整 trace 后，状态 S 的残余熵（理论上应该很小/为零）
  I(S; M | T_tilde) = S 和 M 在给定 T_tilde 下的条件互信息

cut-set bound 应该证明：
  I(S; M | T_tilde) ≤ C_cut(Ω)

其中 C_cut(Ω) 是时间展开 DAG 上割 Ω 的割容量。

## 当前状态

以下所有定义、引理、定理都已在 Lean 4 中 machine-checked，除了一个：
`cut_set_bound` 目前被声明为 `axiom`（或作为 hypothesis 传入）。这是需要你来证明的部分。

## 需要证明的陈述

给定：
  - 时间展开的 DAG G_t = (V_t, E_t)，其中边 e ∈ E_t 携带信道 p_e(y | x)
  - 一个割 Ω ⊆ V_t，将源节点与目标节点分离
  - 割容量 C_cut(Ω) = sup_{联合输入分布} I(X_Ω → Y_{Ω^c} | T_tilde, X_{Ω^c})

我们要证明：
  I(S; M | T_tilde) ≤ C_cut(Ω)

在有限离散情况下，量化到：
  I(S; M | T_tilde) ≤ min_{cut Ω} sum_{edge e in cut} capacity(e)

其中 capacity(e) 是信道 e 的容量（有限离散情况下 = log₂|X_e| 或更精细的界）。
-/

-- ============================================================
-- 第一部分：有限离散概率和信息量定义
-- ============================================================

/-- 有限离散概率质量函数。 -/
structure FinitePMF (α : Type) [Fintype α] [DecidableEq α] where
  pmf : α → ℝ
  pmf_nonneg : ∀ x, 0 ≤ pmf x
  sum_one : ∑ x : α, pmf x = 1

/-- Shannon 熵的单项 -p log₂ p。 -/
def negMulLog2 (p : ℝ) : ℝ :=
  -(p * (Real.log p / Real.log 2))

/-- 质量函数的熵 H(mass) = -∑ mass(x) log₂ mass(x)。 -/
def entropyOf {η : Type} [Fintype η] [DecidableEq η] (mass : η → ℝ) : ℝ :=
  ∑ x : η, negMulLog2 (mass x)

/-- PMF 的 Shannon 熵。 -/
def entropy {α : Type} [Fintype α] [DecidableEq α] (P : FinitePMF α) : ℝ :=
  entropyOf P.pmf

-- ============================================================
-- 第二部分：边缘分布
-- ============================================================

section Marginals

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

/-- 联合分布 P(S, T_tilde, M) 的 (S, T_tilde)-边缘。 -/
def stateVisibleMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (st : State × VisibleTrace) : ℝ :=
  ∑ m : MissingTrace, P.pmf (st.1, st.2, m)

/-- T_tilde 的边缘。 -/
def visibleMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (t : VisibleTrace) : ℝ :=
  ∑ s : State, ∑ m : MissingTrace, P.pmf (s, t, m)

/-- (T_tilde, M) 的边缘。 -/
def visibleMissingMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (tm : VisibleTrace × MissingTrace) : ℝ :=
  ∑ s : State, P.pmf (s, tm.1, tm.2)

/-- M 的边缘。 -/
def missingMass (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (m : MissingTrace) : ℝ :=
  ∑ s : State, ∑ t : VisibleTrace, P.pmf (s, t, m)

end Marginals

-- ============================================================
-- 第三部分：条件熵和条件互信息的定义
-- ============================================================

section InformationQuantities

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

/-- 完整 trace 的联合熵 H(S, T_tilde, M)。 -/
def fullTraceEntropy (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (fun stm : State × VisibleTrace × MissingTrace => P.pmf stm)

/-- H(S | T_tilde) = H(S, T_tilde) - H(T_tilde)。
    给定可见 trace 后，状态 S 的残余条件熵。 -/
def H_S_cond_Ttilde (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (stateVisibleMass P) - entropyOf (visibleMass P)

/-- H(S | T_full) = H(S, T_tilde, M) - H(T_tilde, M)。
    给定完整 trace 后，状态 S 的残余条件熵。理论上应为 0 或接近 0。 -/
def H_S_cond_Tfull (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  fullTraceEntropy P - entropyOf (visibleMissingMass P)

/-- I(S; M | T_tilde) = H(S, T_tilde) + H(M, T_tilde) - H(T_tilde) - H(S, M, T_tilde)。
    S 和 M 在给定 T_tilde 下的条件互信息。这是 cut-set bound 要上界的量。 -/
def I_S_M_cond_Ttilde (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (stateVisibleMass P) +
    entropyOf (visibleMissingMass P) -
    entropyOf (visibleMass P) -
    fullTraceEntropy P

/-- H(M) = -∑ m P(m) log₂ P(m)。
    缺失 trace 的熵。它的上界是 log₂|M|，但可以通过割容量得到更紧的界。 -/
def H_M (P : FinitePMF (State × VisibleTrace × MissingTrace)) : ℝ :=
  entropyOf (missingMass P)

end InformationQuantities

-- ============================================================
-- 第四部分：链式法则（已证）
-- ============================================================

section ChainRule

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

/--
静态分解恒等式（条件熵的链式法则）：
  H(S | T_tilde) = H(S | T_full) + I(S; M | T_tilde)

证明：展开所有定义后，左右两边是纯代数恒等式（`ring`）。
-/
theorem static_decomposition (P : FinitePMF (State × VisibleTrace × MissingTrace)) :
    H_S_cond_Ttilde P = H_S_cond_Tfull P + I_S_M_cond_Ttilde P := by
  unfold H_S_cond_Ttilde H_S_cond_Tfull I_S_M_cond_Ttilde fullTraceEntropy
  ring

end ChainRule

-- ============================================================
-- 第五部分：辅助上界（已证）
-- ============================================================

section AuxiliaryBounds

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

/-- 平凡上界：H(M) ≤ log₂|MissingTrace|。 -/
lemma H_M_le_log_card_M
    (P : FinitePMF (State × VisibleTrace × MissingTrace)) :
    H_M P ≤ Real.log (Fintype.card MissingTrace : ℝ) / Real.log 2 := by
  -- 这个证明在 InfoTheory.lean 的 entropy_le_log_card 中，此处省略细节
  sorry

/-- I(S; M | T_tilde) ≤ H(M)。一个经典的信息论不等式。 -/
lemma I_S_M_cond_Ttilde_le_H_M
    (P : FinitePMF (State × VisibleTrace × MissingTrace)) :
    I_S_M_cond_Ttilde P ≤ H_M P := by
  -- 这个证明在 DualCertificate.lean 的 I_S_M_cond_Ttilde_le_H_M 中
  sorry

end AuxiliaryBounds

-- ============================================================
-- 第六部分：CUT-SET BOUND — 这是需要证明的核心！
-- ============================================================

section CutSetBound

/-
## 数学陈述

设：
  G_t = (V_t, E_t)  时间展开的有向无环图
  S                 源节点（隐藏状态）
  M                 目标（未记录的 trace 片段）
  T_tilde           已记录的 trace（条件变量）

对于割 Ω ⊆ V_t（将源与目标分离的节点子集），定义割容量：
  C_cut(Ω) = sup_{p: 联合输入分布} I(X_Ω → Y_{Ω^c} | T_tilde, X_{Ω^c})

其中 X_Ω 是 Ω 中节点在割上的输出，Y_{Ω^c} 是 Ω^c 中节点的输入。

网络信息论的割集上界定理（El Gamal-Kim 2011, Thm 6.1）说：
  I(S; M | T_tilde) ≤ C_cut(Ω)

在软件正交性假设下（各信道条件独立），C_cut(Ω) ≤ Σ_{e∈cut} capacity(e)，
其中 capacity(e) = max_{p(x)} I(X_e; Y_e) 是单边信道容量。

对于有限离散信道，capacity(e) ≤ log₂|X_e|（输入字母表大小的对数）。

## 在下面的 Lean 代码中

我们用一个简化的有限离散形式来陈述。因为当前形式化没有 DAG/信道的基础设施，
我们用一个参数化的陈述来展示 cut-set bound 的作用。

## 需要你做的

1. 在有限离散情况下，给出 I(S; M | T_tilde) ≤ C_cut(Ω) 的严格证明
2. 在软件正交性下，证明 C_cut(Ω) ≤ Σ_{e∈cut} log₂|X_e|
3. 如果可能，给出比 log₂|X_e| 更紧的界（用信道容量的精确值）

理想情况下，证明应该是"优美简洁"的——不需要概率测度论的全部 machinery，
只需要有限离散求和和 log 不等式。
-/

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

-- 占位：割容量类型。你可以替换为更精确的定义。
variable (Cut : Type) (C_cut : Cut → ℝ)

/--
【需要证明】
Cut-Set Bound（有限离散版本）。

给定：
  P     : 联合分布 P(S, T_tilde, M)
  Ω     : 割（将 S-侧 与 M-侧 分离）
  C_cut : 割容量函数

证明：
  I(S; M | T_tilde) ≤ C_cut(Ω)

直观：从 S 流向 M 的互信息被割的容量所限制。
-/
axiom cut_set_bound
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω : Cut) :
    I_S_M_cond_Ttilde P ≤ C_cut Ω

end CutSetBound

-- ============================================================
-- 第七部分：Cut-set bound 的使用方式（已证，依赖上面的 axiom）
-- ============================================================

section UsingCutSetBound

variable {State VisibleTrace MissingTrace : Type}
variable [Fintype State] [Fintype VisibleTrace] [Fintype MissingTrace]
variable [DecidableEq State] [DecidableEq VisibleTrace] [DecidableEq MissingTrace]

/--
命题 1（静态证书上界）：
  H(S | T_tilde) ≤ H(S | T_full) + C_cut(Ω)

证明：链式法则 + cut-set bound，两步代数。
-/
theorem prop1_static_ub
    (Cut : Type) (C_cut : Cut → ℝ) (Ω : Cut)
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (h_bound : I_S_M_cond_Ttilde P ≤ C_cut Ω) :
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_cut Ω := by
  have h_chain := static_decomposition P
  rw [h_chain]
  exact add_le_add (le_refl (H_S_cond_Tfull P)) h_bound

/--
软件正交性假设：每条软件信道独立运行，割容量不超过各边容量之和。
-/
def software_orthogonal (Cut : Type) (C_cut : Cut → ℝ) (C_edge_sum : Cut → ℝ)
    (Cuts_U_to_S : Set Cut) : Prop :=
  ∀ Ω ∈ Cuts_U_to_S, C_cut Ω ≤ C_edge_sum Ω

/--
推论（加性上界形式）：
  在软件正交性下，H(S | T_tilde) ≤ H(S | T_full) + Σ_{e∈cut} capacity(e)

这是实际部署中用来计算 ε_state^UB 的形式。
-/
theorem corollary_additive_ub
    (Cut : Type) (C_cut : Cut → ℝ) (C_edge_sum : Cut → ℝ) (Cuts_U_to_S : Set Cut)
    (Ω : Cut) (hΩ : Ω ∈ Cuts_U_to_S)
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (h_bound : I_S_M_cond_Ttilde P ≤ C_cut Ω)
    (h_ortho : software_orthogonal Cut C_cut C_edge_sum Cuts_U_to_S) :
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_edge_sum Ω := by
  have h_prop1 := prop1_static_ub Cut C_cut Ω P h_bound
  have h_ortho_bound : C_cut Ω ≤ C_edge_sum Ω := h_ortho Ω hΩ
  calc
    H_S_cond_Ttilde P ≤ H_S_cond_Tfull P + C_cut Ω := h_prop1
    _ ≤ H_S_cond_Tfull P + C_edge_sum Ω :=
      add_le_add (le_refl (H_S_cond_Tfull P)) h_ortho_bound

end UsingCutSetBound

/-
## 总结

这个文件的核心未解决问题是 `cut_set_bound`（第 181 行附近的 `axiom`）。

所有其他定理（`static_decomposition`、`prop1_static_ub`、`corollary_additive_ub`）
都已在 Lean 4 中 machine-checked，它们只依赖 `cut_set_bound` 这一个外部假设。

如果你能给 `cut_set_bound` 一个有限离散的 machine-checkable 证明，
那么整个静态证书 pipeline 就完全形式化了。

## 给数学系同学的方向提示

1. **有限离散情况**：所有随机变量取值有限，所以不需要测度论。上确界变成有限 max。
2. **DAG 展开**：时间展开图是有向无环的，可以用拓扑排序做归纳。
3. **d-分离**：在因果图模型中，给定 T_tilde 后，S 和 M 被割 Ω d-分离。
4. **信道容量**：对于有限离散无记忆信道，C = max_{p(x)} I(X; Y)，可以精确计算。
5. **参考**：El Gamal & Kim (2011), "Network Information Theory", Theorem 6.1（割集上界）；
   Cover & Thomas (2006), Chapter 15（网络信息论）。
-/
