# DAG 马尔可夫性质与信道容量自动化推导

> **实现状态标注**：
> - ✅ 已落实为 Lean 代码
> - ⏳ 部分落实（已有框架，核心算法待补全）
> - ❌ 待实现（属于 follow-up 论文范围）

## 一、DAG 条件独立性理论基础  ❌

### 1. DAG 的基本依赖关系

在DAG中，每个节点代表一个随机变量，有向边表示变量间的直接依赖关系。根据贝叶斯网络的定义，DAG中每个节点\(X_i\)满足以下局部马尔可夫性质：

\[
X_i \perp \text{Nd}(X_i) \mid \text{Pa}(X_i)
\]

其中：
- \(\text{Pa}(X_i)\)是\(X_i\)的父节点集合
- \(\text{Nd}(X_i)\)是\(X_i\)的非后裔节点集合
- \(\perp\)表示条件独立

这意味着每个变量仅依赖于其父节点，而与非后裔节点条件独立。这一性质是信息论中马尔可夫边界和马尔可夫毯概念的基础。

### 2. 马尔可夫毯的理论基础

马尔可夫毯(Markov Blanket)是DAG中一个关键概念，定义为：

\[
\text{MB}(X) = \text{Pa}(X) \cup \text{Ch}(X) \cup \text{Pa}(\text{Ch}(X))
\]

其中：
- \(\text{Ch}(X)\)是\(X\)的子节点集合
- \(\text{Pa}(\text{Ch}(X))\)是子节点的父节点集合

马尔可夫毯具有以下重要性质：**给定马尔可夫毯，节点\(X\)与其他所有节点条件独立**。更重要的是，马尔可夫毯是满足这一条件的最小集合，这使得它成为信息论中推导条件独立性的理想工具。

### 3. d-separation算法：条件独立性验证

d-separation(方向分离)是验证DAG中两组节点是否条件独立的算法，基于以下三种基本结构：
- 链结构\(X \rightarrow Y \rightarrow Z\)：若观察到中间节点\(Y\)，则\(X\)与\(Z\)条件独立
- 叉结构\(X \leftarrow Y \rightarrow Z\)：若观察到共同祖先\(Y\)，则\(X\)与\(Z\)条件独立
- 碰撞结构\(X \rightarrow Y \leftarrow Z\)：若未观察到\(Y\)或其后裔，\(X\)与\(Z\)条件独立

通过d-separation算法，可以系统性地验证DAG中所有可能的条件独立性声明，从而为h_markov的自动生成提供理论基础。

## 二、h_markov的自动生成方法  ❌

h_markov代表满足条件马尔可夫性的变量集合，其自动生成需要结合DAG结构解析和条件独立性验证。以下是具体实现步骤：

### 1. DAG结构解析

首先需要将DAG的结构表示转换为计算可用的形式，通常采用邻接矩阵或邻接表表示：

```lean
def DAGtoAdjacencyMatrix (G : DAG) : Matrix ℕ ℕ ℝ := ...
```

通过遍历DAG的节点和边，构建每个节点的父节点集合(\(\text{Pa}(X)\))和非后裔集合(\(\text{Nd}(X)\))：

```lean
def findParents (G : DAG) (X : ℕ) : Finset ℕ := ...
def findNonDescendants (G : DAG) (X : ℕ) : Finset ℕ := ...
```

### 2. 马尔可夫毯自动推导

基于d-separation算法，可以自动推导每个节点的马尔可夫毯：

```lean
def computeMarkovBlanket (G : DAG) (X : ℕ) : Finset ℕ := by
  let PaX := findParents G X
  let ChX := findChildren G X
  let SpX := findSpouses G X
  exact PaX ∪ ChX ∪ SpX
```

其中，配偶节点(Spouses)是与\(X\)有共同子节点的节点，这是碰撞结构中的关键概念。

### 3. 条件独立性声明生成

利用马尔可夫毯信息，可以自动生成满足条件独立性的声明集合：

```lean
def generateMarkovConditions (G : DAG) : List (Finset ℕ × Finset ℕ × Finset ℕ) := by
  let nodes := G.nodes
  let mut conditions := []
  for X in nodes do
    let MBX := computeMarkovBlanket G X
    let A := nodes \ MBX
    let B := nodes \ (MBX ∪ {X})
    let C := MBX
    conditions := conditions ++ [(A, B, C)]
  return conditions
```

这一过程确保生成的条件独立性声明满足全局马尔可夫性质，即对于任何两组不相交的节点集合\(A\)和\(B\)，如果\(A\)和\(B\)被\(C\)所d-separates，则\(A \perp B \mid C\)。

### 4. h_markov的代码表示

在用户提供的代码框架中，h_markov可以通过以下方式表示：

```lean
def h_markov (G : DAG) (P : FinitePMF (State × VisibleTrace × MissingTrace)) : Prop := by
  let conditions := generateMarkovConditions G
  let mut markovDecls := true
  for (A, B, C) in conditions do
    markovDecls := markovDecls ∧ (A ⊥ B | C) under P
  return markovDecls
```

其中，`(A ⊥ B | C)`表示在给定条件\(C\)下，集合\(A\)与集合\(B\)条件独立的命题声明。

## 三、信道容量\(h_{\text{cap}}\)的计算方法  ⏳

信道容量\(h_{\text{cap}}\)的计算是信息论中的经典问题，对于给定的信道转移概率\(p(y|x)\)，其定义为：

\[
h_{\text{cap}} = \max_{p(x)} I(X;Y)
\]

其中\(I(X;Y)\)是输入\(X\)与输出\(Y\)之间的互信息。互信息的计算公式为：

\[
I(X;Y) = \sum_{x,y} p(x,y) \log \frac{p(x,y)}{p(x)p(y)} = \sum_{x,y} p(x,y) \log \frac{p(y|x)}{p(y)}
\]

由于\(p(y) = \sum_x p(x)p(y|x)\)，互信息也可以表示为：

\[
I(X;Y) = H(X) - H(X|Y)
\]

其中\(H(X)\)是输入的熵，\(H(X|Y)\)是条件熵。

### 1. 离散信道的信道容量计算

对于离散输入输出信道，计算\(h_{\text{cap}}\)的标准方法是Blahut-Arimoto算法。该算法通过迭代优化输入分布\(p(x)\)，最大化互信息\(I(X;Y)\)。

Blahut-Arimoto算法的迭代步骤如下：

1. **初始化输入分布**：通常选择均匀分布\(p^{(0)}(x) = 1/|X|\)。
2. **计算对偶变量**：
   \[
   r^{(t+1)}(x) = \exp\left( \sum_{y} p^{(t)}(y) \log \frac{p(y|x)}{p^{(t)}(y)} \right)
   \]
3. **更新输入分布**：
   \[
   p^{(t+1)}(x) = \frac{r^{(t+1)}(x)}{\sum_{x'} r^{(t+1)}(x')}
   \]
4. **计算互信息**：
   \[
   I^{(t)}(X;Y) = \log \sum_{x} r^{(t+1)}(x)
   \]
5. **收敛判断**：当连续两次迭代的互信息差值小于预设阈值(如\(10^{-6}\))时停止迭代。

### 2. 基于DAG约束的信道容量优化

在DAG约束下，信道容量的计算变得更加复杂，因为输入分布\(p(x)\)需要满足DAG中定义的条件独立性约束。这种约束下的信道容量计算可以表示为：

\[
h_{\text{cap}}^{\text{DAG}} = \max_{p(x) \in \mathcal{P}_{\text{DAG}}} I(X;Y)
\]

其中\(\mathcal{P}_{\text{DAG}}\)是满足DAG条件独立性约束的概率分布集合。

**在用户代码框架中，pmf_from_vars函数已经实现了从原始变量到包含中间变量的四元组分布的映射**：

```lean
def pmf_from_vars {CutVars : Type} [Fintype CutVars] [DecidableEq CutVars]
    (P : FinitePMF (State × VisibleTrace × MissingTrace))
    (Ω_vars : (State × VisibleTrace × MissingTrace) → CutVars) :
    FinitePMF (State × CutVars × MissingTrace × VisibleTrace) := ...
```

这为基于DAG约束的信道容量计算提供了基础。通过这个函数，可以将原始分布\(p(x)\)映射到满足DAG条件独立性的分布\(p(x', \omega)\)，其中\(\omega\)是中间变量集合。

### 3. 自动化计算流程  ✅（Kernel 已实现）

基于用户代码框架，\(h_{\text{cap}}\)的计算可以分为以下几个步骤：

1. **定义信道转移概率**：在代码中定义\(p(y|x)\)的函数或表格。
2. **初始化输入分布**：使用均匀分布或其他先验分布初始化\(p(x)\)。
3. **DAG约束应用**：通过pmf_from_vars函数将原始分布映射到满足DAG条件独立性的分布。 ✅（`CutSetBoundExtract.lean`）
4. **Blahut-Arimoto迭代**：应用Blahut-Arimoto算法迭代优化输入分布，在每一步都应用DAG约束。 ❌（BA算法本身未在Lean中形式化；外部Python计算 + KKT证书核验路径已实现于`ChannelCapacity.lean`）
5. **互信息计算**：利用marginalXWMass_eq_stateVisibleMass等引理计算满足DAG约束的互信息。 ✅（`CutSetBoundExtract.lean`）

## 四、DAG到h_markov的自动化推导工具设计  ❌

### 1. 框架整体架构

设计一个自动化推导DAG到h_markov的工具，需要考虑以下核心模块：

1. **DAG解析器**：负责读取和解析DAG结构，提取节点和边关系。
2. **依赖关系分析器**：基于d-separation算法分析变量间的依赖关系。
3. **马尔可夫条件生成器**：根据依赖关系分析结果生成满足条件独立性的命题声明。
4. **信道容量计算器**：实现Blahut-Arimoto算法，计算满足DAG约束的信道容量。

### 2. DAG解析模块实现

DAG解析模块需要将DAG的图形结构转换为计算可用的形式。对于用户提供的代码框架，可以采用以下实现方式：

```lean
namespace DAGParser

structure DAG where
  nodes : Finset ℕ
  edges : Finset (ℕ × ℕ)
  acyclic : WellFounded (λ x y => (x, y) ∈ edges)

def findParents (G : DAG) (X : ℕ) : Finset ℕ := by
  let mut parents := Finset.empty ℕ
  for (u, v) in G.edges do
    if v = X then
      parents := parents ∪ {u}
  return parents

def findNonDescendants (G : DAG) (X : ℕ) : Finset ℕ := by
  let descendants := findDescendants G X
  return G.nodes \ (descendants ∪ {X})

def findDescendants (G : DAG) (X : ℕ) : Finset ℕ := by
  let mut descendants := Finset.empty ℕ
  let mut stack := [X]
  while ¬ stack为空 do
    let current := stack.pop
    for (u, v) in G.edges do
      if u = current ∧ v ∉ descendants then
        descendants := descendants ∪ {v}
        stack := stack ++ [v]
  return descendants

end DAGParser
```

### 3. 马尔可夫条件生成器实现

基于DAG解析的结果，马尔可夫条件生成器可以自动生成满足条件独立性的命题声明：

```lean
namespace MarkovGenerator

def isDSeparated (G : DAG) (A B C : Finset ℕ) : Prop := by
  -- 实现d-separation算法
  -- 检查所有可能的路径是否被C所阻断

def generateMarkovDecls (G : DAG) : List Prop := by
  let nodes := G.nodes
  let mut declarations := []
  for X in nodes do
    let PaX := DAGParser.findParents G X
    let NdX := DAGParser.findNonDescendants G X
    let C := PaX
    let A := {X}
    let B := NdX
    let declaration := A ⊥ B | C under P
    declarations := declarations ++ [declaration]
  return declarations

end MarkovGenerator
```

### 4. 信道容量计算模块实现  ⏳（KKT框架已实现，BA算法未形式化）

结合用户代码框架中的`FinitePMF`和`pmf_from_vars`，可以实现以下信道容量计算模块。

> `KKT_Certificate` 结构和 `capacity_le_of_kkt` 定理已实现于 `ChannelCapacity.lean`。
> Blahut-Arimoto 迭代本身（`updateInputDistribution`、收敛性证明）未在Lean中形式化，
> 采用外部Python计算 + Lean核验KKT证书的策略。

```lean
namespace ChannelCapacity

def updateInputDistribution (P_prev : FinitePMF α) (Pyx : α → β → ℝ) (Py : β → ℝ) : FinitePMF α := by
  let P_new x := exp(∑ y, Pyx x y * log (Pyx x y / Py y)) / ∑ x', exp(∑ y, Pyx x' y * log (Pyx x' y / Py y))
  -- 需要处理数值稳定性问题

def mutualInformation (Pxy : FinitePMF (α × β)) (Py : β → ℝ) : ℝ := by
  ∑ x y, Pxy.pmf (x, y) * log (Pxy.pmf (x, y) / (Pxy.marginalX x * Pxy.marginalY y))

def computeChannelCapacity (G : DAG) (Pyx : α → β → ℝ) (ε : ℝ) : ℝ × FinitePMF α := by
  let P0 x := 1 / G.nodes.length
  let P_prev := FinitePMF.ofFn P0
  let mut P_current := P_prev
  let mut I_prev := 0
  let mut I_current := mutualInformation (pmf_from_vars P_prev Ω_vars) (marginalWMass (pmf_from_vars P_prev Ω_vars))
  while |I_current - I_prev| > ε do
    let P_current := updateInputDistribution P_prev Pyx (marginalWMass (pmf_from_vars P_prev Ω_vars))
    I_prev := I_current
    I_current := mutualInformation (pmf_from_vars P_current Ω_vars) (marginalWMass (pmf_from_vars P_current Ω_vars))
  return (I_current, P_current)

end ChannelCapacity
```

## 五、实现案例与验证方法  ✅

### 1. 简单DAG案例  ✅（CaseStudy.lean 线性链）

考虑一个简单的DAG结构：\(X \rightarrow Y \rightarrow Z\)。根据DAG的局部马尔可夫性质，可以自动生成以下条件独立性声明：

- \(X \perp Z \mid Y\)
- \(Y \perp X \mid \emptyset\)（自动满足）
- \(Y \perp Z \mid \emptyset\)（自动满足）
- \(Z \perp X \mid Y\)

这些声明可以自动编码为h_markov的命题集合。

### 2. 验证方法

为确保自动生成的h_markov和计算的\(h_{\text{cap}}\)正确，可以采用以下验证方法：

1. **理论验证**：检查生成的条件独立性声明是否符合d-separation准则。
2. **数值验证**：对于已知信道容量的简单信道(如二进制对称信道)，检查计算结果是否与理论值一致。
3. **边界测试**：测试极端情况下的信道容量，如噪声完全消除时信道容量应等于输入熵。

## 六、高级主题  ❌

### 1. d-separation算法原理

d-separation算法基于图论中的路径阻断概念，判断给定条件变量Z是否存在路径将X与Y连接。其基本规则如下：

- **链式结构(X→Z→Y)**：若路径为X→Z→Y，则Z阻断该路径，即X⊥Y|Z
- **叉式结构(X←Z→Y)**：同样，Z阻断路径X⊥Y|Z
- **碰撞结构(X→Z←Y)**：Z不阻断该路径；若Z的后代在路径上，则路径仍不被阻断

**关键洞察**：在DAG中，若Z是X到Y的割集，即所有从X到Y的路径必须经过Z，那么X与Y在给定Z的条件下必然独立。这正是h_markov的理论基础。

### 2. 自动推导算法实现

基于上述理论，我们可以设计一个高效的自动推导算法：

```lean
def autoGenerateMarkovConditions (G : DAG) : List (Set Var × Set Var × Set Var) := by
  let mut conditions : List (Set Var × Set Var × Set Var) := []
  for X in G nodes do
    for Y in G nodes do
      if X ≠ Y ∧ ¬G.存在边(X,Y) ∧ ¬G.存在边(Y,X) then
        let MB_X := computeMarkovBlanket X
        let MB_Y := computeMarkovBlanket Y
        let Z_candidate := MB_X ∩ MB_Y
        if G.dSeparates(X,Y,Z_candidate) then
          conditions ← (X,Y,Z_candidate) :: conditions
  return conditions
```

该算法的核心在于**马尔可夫毯的计算**和**d-separation的验证**。马尔可夫毯是变量的最小割集，包含其父节点、子节点及其子节点的父节点。通过先计算马尔可夫毯，再检查其交集是否能阻断所有路径，可以高效地生成所有可能的条件独立性约束。

### 3. 复杂度优化与马尔可夫毯生成

直接应用d-separation算法的复杂度为O(n³)，对于大规模DAG可能不切实际。因此，我们采用**马尔可夫毯生成算法**进行优化：

- **Grow-Shrink算法**：通过先扩展后收缩的方式生成马尔可夫毯，复杂度为O(n²+b²n)，其中b为最大马尔可夫毯的大小
- **IAMB算法**：基于条件互信息排序的迭代算法，复杂度更低，适合大规模DAG

### 4. 信道容量h_cap的精确计算

信道容量h_cap是衡量信息传递效率的关键指标，在离散信道模型中可通过互信息最大化来计算。

#### 4.1 条件互信息的数学表达

条件互信息I(Y;Z|W)表示在已知W的条件下，Y与Z之间的相互依赖程度：

```
I(Y;Z|W) = H(Y|W) - H(Y|Z,W)
         = ∑_{y,z,w} p(y,z,w) log [p(y|z,w)/p(y|w)]
```

对于用户代码中的`I_YZ_W`，它对应于`I(Y;Z|W)`，而`h_cap`则是该互信息的最大值，即：

```
h_cap = max_{p(x)} I(Y;Z|W)
```

#### 4.2 Blahut-Arimoto算法的条件扩展

对于条件互信息最大化问题，我们将Blahut-Arimoto算法扩展为：

1. **初始化**：选择初始输入分布p(x)
2. **更新条件分布**：
   ```
   q(y|x) = [p(y|x) * exp(λ_y)] / [∑_{x'} p(y|x') * exp(λ_{x'})]
   ```
3. **更新输入分布**：
   ```
   p(x) ∝ exp(∑_y q(y|x) log [p(y|x)/q(y|x)])
   ```
4. **计算当前互信息**：收敛判断

#### 4.3 DAG结构对信道容量的影响

DAG的拓扑结构直接影响联合分布的分解方式，从而影响信道容量的计算：

- **若Z仅依赖于Y**：条件互信息退化为无条件互信息I(Y;Z)
- **若W是X的函数**：联合分布可分解为p(x) p(y|x) p(z|y) p(w|x)
- **若存在路径X→Y→Z**：根据数据处理不等式(DPI)，I(X;Z|W) ≤ I(X;Y|W)

### 5. DAG中的数据处理不等式(DPI)与信息瓶颈

数据处理不等式指出信息处理不会增加随机变量间的依赖程度。在DAG中：

```
若存在路径X→Y→Z，则I(X;Z|W) ≤ I(X;Y|W)
```

**证明**：基于互信息的链式法则和条件独立性。

割集Y作为信息瓶颈的作用体现在：
- **信息保留能力**：Y保留了从X到Z的最大信息流
- **隐私保护作用**：通过限制Y的信息容量，可以间接控制Z的信息泄漏
- **最小熵耦合**：在给定信息保留要求下，Y的熵最小化

### 6. 从DAG自动推导h_markov条件的完整算法

综合以上分析，完整算法的核心步骤：

1. 计算所有节点的马尔可夫毯
2. 遍历所有非邻接节点对
3. 寻找最小割集Z
4. 验证Z是否d-separates X和Y
5. 收集所有条件独立性约束

**马尔可夫毯计算**：
```
computeMarkovBlanket(v) = Pa(v) ∪ Ch(v) ∪ Pa(Ch(v))
```

**d-separation验证**：通过祖先子图构建、道德化处理、删除Z节点、检查X与Y连通性四步完成。

**割集优化**：通过贪心算法从候选割集中逐步移除冗余元素。

### 7. 抽象Cut-Set Bound定理

抽象Cut-Set Bound定理是连接拓扑瓶颈(DPI)与具体容量上界(h_cap)的桥梁：

```
I(S;M|T_tilde) ≤ I(Y;Z|W) ≤ h_cap
```

**证明思路**：
1. **DPI应用**：由于Y是X到Z的割集，I(X;Z|W) ≤ I(X;Y|W)
2. **信道容量定义**：h_cap被定义为I(Y;Z|W)的最大值
3. **传递性**：通过信息不等式的传递性

## 七、系统实现与验证  ⏳

### 1. h_markov的系统实现

在用户提供的Lean代码中，h_markov通过`condMarkov`参数表示。

### 2. h_cap的系统实现

通过应用Blahut-Arimoto算法计算条件互信息最大值，并验证结果是否满足理论预期。

### 3. 系统验证方法

- **合成数据测试**：生成具有已知条件独立性的DAG
- **理论值对比**：将计算结果与已知信道的理论容量值进行对比
- **收敛性分析**：分析算法在不同初始分布和约束条件下的收敛性
- **鲁棒性测试**：测试算法在噪声干扰和有限样本情况下的性能
