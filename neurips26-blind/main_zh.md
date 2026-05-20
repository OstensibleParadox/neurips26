# 智能体审计的双重证书：分离结构不可恢复性与决策相关性

## 摘要

对已部署的语言模型智能体进行审计，需要两个可分离的量：多少有效操作状态逃逸了记录轨迹，以及这些残差状态中有多少驱动了行为。本文提出一个双重证书协议（dual-certificate protocol）。静态证书 $\varepsilon_{\text{state}}^{\text{UB}}$ 通过未追踪信道上的最小割对残差隐状态熵给出上界。动态证书 $\delta_{\text{act}}^{\text{LB}}$ 通过一个在条件数据处理不等式（conditional DPI）框架下可容许的探针分类体系——重放（replay）、干预（intervention）、代理（proxy）——对残差决策相关性给出下界。这两个轴是独立的。在 ReAct 实验中，日志记录将静态边界从 $16{,}464$ 位逐步消减至 $0$ 位；受控重放将休眠计算器任务与活跃规划任务在相同拓扑下区分开来——软策略偏移为 $0.0163$ 位，95\% CI $[0.0124,0.0208]$——argmax 工具选择保持不变。将 $\delta_{\text{act}}^{\text{LB}}$ 索引化到隐信道坐标上，即得到一个激活剖面（activation profile）。在 LLaDA 去噪轨迹上，扰动在早期步骤中保持接近底线，并在最终绑定步骤升至 $0.110$ 位（95\% CI $[0.052,0.234]$）。在多智能体通信边上，交换一个 Worker 的私人报告给出 $0.901$ 位（95\% CI $[0.873,0.928]$）。一个 Lean 4 工件对自回归零割情形进行了机械化验证，并从 Mathlib 第一原理证明了条件 DPI 和链式法则归约，仅割集容量上界保留为外生结构前提。

## 关键词

智能体审计（agent audit）、双重证书（dual certificates）、结构不可恢复性（structural unrecoverability）、决策相关性（decision relevance）、条件数据处理不等式（conditional DPI）、割集上界（cut-set bound）、自回归零割（autoregressive zero-cut）、Lean 4 形式化

## 一、引言

考虑一个 ReAct 风格的智能体，配有一个每轮容量为 $16{,}384$ 位的未登录草稿板（scratchpad）。输出轨迹上的回归测试显示无行为变化，然而在受控重放下禁用草稿板后的同一条轨迹，揭示了规划任务上工具令牌概率分布中 $0.0163$ 位的偏移。这一差异不是探针伪影。它是审计的一个结构特征：记录轨迹未能区分两个性质上不同的系统——一个其隐藏容量在测试分布上处于休眠状态，另一个其隐藏容量处于活跃状态。识别哪一个成立，正是审计的任务。

这是两个不同的量：多少内部状态逃逸了轨迹，以及其中多少驱动了下一步行动。仅依赖输出的黑盒审计视图会将它们合并为一个既不可计算也不具诊断性的单一「隐藏性」判断。一个拥有大日志缺口但无行为性隐藏驱动的系统，与一个拥有小缺口但强驱动的系统是无法区分的，尽管二者的审计含义截然不同。

本文提出一个双重证书协议，分别回答每个问题。静态证书 $\varepsilon_{\text{state}}^{\text{UB}}$ 仅依据部署拓扑，通过未追踪信道上的割集界对残差熵 $H(S_t \mid \tilde T_t)$ 给出上界。动态证书 $\delta_{\text{act}}^{\text{LB}}$ 通过三种探针类别之一（重放、干预或代理，取决于审计者的访问权限）对残差决策相关性 $I(S_t; A_t \mid \tilde T_t)$ 给出下界。这两个证书是独立的轴：一个 $\varepsilon_{\text{state}}^{\text{UB}}$ 大而 $\delta_{\text{act}}^{\text{LB}}$ 小的系统具有不可恢复但处于休眠状态的状态；两个都大的系统则具有不可恢复且活跃的状态。两者都是可审计的。两者都不是单个标量所能揭示的。

动态轴亦可被索引化。审计者不仅可追问残差状态是否重要，还可追问它在*何处*重要：哪个模块、哪个去噪步骤或哪个通信边承载了决策相关性。这将证书从标量诊断转化为部署隐藏状态几何上的激活剖面。

以 $\tilde T_t$ 为条件本身就是保护措施的一部分，而非干扰项。如果一个模型将隐写或压缩式推理写入记录轨迹，则该信息位于 $\tilde T_t$ 中，并被 $I(S_t; A_t \mid \tilde T_t)$ 条件化移除。动态证书衡量的是超越已记录轨迹的残差决策相关性；它不计数已经对审计记录可见的隐藏性。

**贡献。** 本文为智能体审计定义了一个双重证书框架 $(\varepsilon_{\text{state}}^{\text{UB}}, \delta_{\text{act}}^{\text{LB}})$。命题~\ref{prop:static-ub} 通过未追踪信道上的最小割给出了残差隐状态熵的拓扑上界。命题~\ref{prop:dynamic-lb} 并非一个新的信息论不等式；它是一个审计归约，将条件 DPI 转化为残差决策相关性的三个可容许下界探针——重放、干预和代理。

我们在三种残差状态几何上评估该协议：一个 ReAct 草稿板模块、一条扩散语言模型去噪轨迹，以及一条多智能体私人报告边。同一计算公式在不同设置中被复用，但索引从模块变为时间步再变为通信边。附录中的校准覆盖了只读代理估计和一个人工合成真实场景，其中静态边界与真实隐藏状态熵相匹配。一个 Lean 4 工件从 Mathlib 第一原理对推论~\ref{cor:auto-exact} 进行了机械化验证，并从有限离散定义证明了迹缺口链式法则和条件 DPI，仅割集容量上界保留为命题~\ref{prop:static-ub} 的外生结构前提（精确边界见 §\ref{sec:external-axioms}）。

## 二、相关工作

**探针、修补与因果抽象。** 因果抽象（causal abstraction）、隐藏知识诱发（latent-knowledge elicitation）、零空间投影（nullspace projection）和遗忘式探针（amnesic probing）是代理式证据的自然来源：当它们暴露一个探针变量 $Z_t = \varphi(S_t)$ 且所需的条件假设成立时，其与行动的互信息可通过代理证书加以解释。因果追踪/ROME、表征工程和激活值添加则提供干预式证据，前提是修补仅通过 $S_t$ 影响行动。

**黑盒审计与网络信息论。** 性质检验和黑盒安全审计研究仅从输出中可以推断出什么。本文的区别在于：仅输出访问可以支持行为测试，但其本身并不为 $\delta_\text{act}$ 提供下界；而当结构访问可用时，$\varepsilon_{\text{state}}^{\text{UB}}$ 仍然可以从拓扑计算得出。静态证书证明将割集上界应用于时间展开 DAG（完整推导见附录~\ref{app:netinfo}）。

**扩散语言模型智能体。** LLaDA 实现了大规模掩码扩散语言建模，具有双向去噪和指令跟随能力。最近的智能体工作进一步研究了多步决策和工具使用流程中的扩散语言模型，包括与自回归智能体的匹配比较。这些系统使中间去噪潜变量成为动态证书的一个天然的非 ReAct 隐藏信道。

## 三、设置与审计机制

标准信息记号遵循 Cover \& Elements。所有对数以 2 为底；熵和互信息以位（bits）报告。

在第 $t$ 步：*完整轨迹* $T_t$（所有中间激活）、*记录轨迹* $\tilde T_t \subseteq T_t$（审计者可见）、*有效状态* $S_t$（内部计算）、*行动* $A_t$（下一令牌）、*未记录源* $U_t$（不在 $\tilde T_t$ 中的外生输入）。

### 3.1 两个核心审计量

*定义（核心审计量）*：双重证书所针对的两个量是：
- **结构不可恢复性：** $\varepsilon_\text{state} := H(S_t \mid \tilde T_t)$，在给定可见轨迹条件下有效状态的残差熵。
- **残差决策相关性：** $\delta_\text{act} := I(S_t; A_t \mid \tilde T_t)$，在给定可见轨迹条件下有效状态与下一行动之间的互信息。

两个量在部署中均不可直接计算：$\varepsilon_\text{state}$ 需要恢复完整的内部状态分布，$\delta_\text{act}$ 需要观测 $S_t$。双重证书框架针对的是：
- 一个*结构上界* $\varepsilon_{\text{state}}^{\text{UB}} \geq \varepsilon_\text{state}$，从部署拓扑计算得出（§\ref{sec:static-cert}）；
- 一个*经验下界* $\delta_{\text{act}}^{\text{LB}} \leq \delta_\text{act}$，通过探针变量估计（§\ref{sec:dynamic-cert}）。

所报告的审计对为 $(\varepsilon_{\text{state}}^{\text{UB}}, \delta_{\text{act}}^{\text{LB}})$。

仅凭行为观察无法识别这两个量：不同的因果图可以在 $(\tilde T_t, A_t)$ 对上产生相同的联合分布，因此观察输出不能固定 $H(S_t \mid \tilde T_t)$ 或 $I(S_t; A_t \mid \tilde T_t)$。静态证书通过拓扑的结构访问解决第一个问题；动态证书通过灰盒探针访问解决第二个问题。

*注（互补性与继承性）*：由数据处理不等式，$\delta_\text{act} \leq \varepsilon_\text{state}$。证书在其各自的有界方向上继承这一排序，但仍然是审计证据的独立轴：
- 若 $\varepsilon_{\text{state}}^{\text{UB}} = 0$（全日志架构），则 $\varepsilon_\text{state} = 0$ 且 $\delta_\text{act} = 0$；任何有效的下界均满足 $\delta_{\text{act}}^{\text{LB}} = 0$。
- 若 $\delta_{\text{act}}^{\text{LB}} = 0$（在最佳可用探针下），隐藏状态可能仍然存在：$\varepsilon_{\text{state}}^{\text{UB}}$ 可能很大，而当前任务并未激活该隐藏容量（休眠不可恢复状态）。逆否命题（$\delta_{\text{act}}^{\text{LB}} > 0 \Rightarrow \varepsilon_{\text{state}}^{\text{UB}} > 0$）由 DPI 排序推出。
因此，审计解释是二维的：部署团队必须同时报告残差信道预算和最强可容许行为探针，而不是将它们坍缩为单一的隐藏性评分。

### 3.2 审计访问模式

1. *结构访问。* 审计者拥有部署架构、日志清单和协议预算。这足以从拓扑计算 $\varepsilon_{\text{state}}^{\text{UB}}$（§\ref{sec:static-cert}），但不提供动态下界。
2. *受控重放访问。* 审计者可以在原样（wild）和重放（replay）状态下重新运行同一系统，同时保持可见轨迹不变。当重放机制仅通过缺失状态恢复影响行动时，这支持重放证书。
3. *代理或干预访问。* 审计者可以读取代理变量 $Z_t = f(S_t)$ 或扰动一个隐藏模块。这些支持关于 $\delta_\text{act}$ 的条件 DPI 下界（§\ref{sec:dynamic-cert}）。

本文的经验核心使用受控 ReAct 智能体中的这些访问模式。它不使用转述式（paraphrase-based）或格式化的黑盒重放作为内部决策相关性的证据。

## 四、静态证书：通过未追踪信道容量的结构上界

静态证书从部署拓扑对 $\varepsilon_\text{state} = H(S_t \mid \tilde T_t)$ 给出上界。不在可见轨迹中但能影响 $S_t$ 的信息必须通过未记录信道传输。对这些信道在最坏情况下容量的有界化，即给出了隐藏状态熵的上界。

### 4.1 时间展开部署图与组件预算

令 $G_t = (V_t, E_t)$ 为截至第 $t$ 步的部署时间展开有向无环图（DAG）。节点是状态更新、工具调用、内存读/写、消息；边是信息信道。三类对象：未记录源 $U_t$（检索结果、外部内存、未记录消息）、可见轨迹 $\tilde T_t$ 和有效状态 $S_t$。令 $\mathcal{C}_\text{unlogged}$ 为所有分隔 $U_t$ 与 $S_t$ 的可达边割集。

一组边称为*软件正交*的，如果在以 $\tilde T_t$ 为条件的联合分布下，信道输出可因式分解：$p(\{y_e\}_{e \in E'} \mid \{x_e\}, \tilde T_t) = \prod_{e \in E'} p(y_e \mid x_e, \tilde T_t)$。当未记录信道使用独立的 API 调用或分离的内存区域时，这一条件成立（非正交情形的补救处理见附录~\ref{app:netinfo}）。

*引理（加性分解）*：在软件正交性且每条边具有预算 $c_e$ 的条件下，诱导割容量可分解为：$C_\text{cut}(\Omega) \leq \sum_{e \in E(\Omega, \Omega^c)} c_e$。

当软件正交性不成立时（例如两条未记录信道共享一个隐藏状态变量），每条边的求和 $\sum_{e \in E(\Omega, \Omega^c)} c_e$ 仍然通过跨耦合信道的互信息次可加性构成 $C_\text{cut}(\Omega)$ 的上界：$I(X_\Omega; Y_{\Omega^c} \mid \tilde T_t, X_{\Omega^c}) \leq \sum_e I(X_e; Y_e \mid \tilde T_t) \leq \sum_e c_e$。正交性是加性分解*紧致性*的要求，而非上界有效性的要求（形式化处理见附录~\ref{app:netinfo}）。

每条边的预算 $c_e$ 从接口规格中读取：对词汇表 $\mathcal{V}$ 上 $K$ 令牌的文本信道为 $K \log |\mathcal{V}|$，对 $d$ 维量化状态为 $d \log Q$，对离散调度器为 $\log |\Omega_\text{states}|$。离散化参数 $Q$ 是审计者的可选参数（本文使用 $Q=256$，即 8 位审计离散化）；更紧或更粗的离散化按比例移动边界而不改变结构论断。所有边预算均为最坏情况（最大熵）预算；更紧的经验预算只会改善证书。

该边界包含三个部分。$\varepsilon_\text{nominal}$ 项是即使在完整内部轨迹下仍然存在的残差不确定性；对于一个完全检测化的软件智能体，此项通常为零。割项是为仍可通过未记录接口进入 $S_t$ 的信息设置的审计预算。有向 MI 符号在形式上为最坏情况信息流定价，而实际实现的证书仅需边预算和部署图未记录部分上的最小割。

*命题（基于割集界的静态证书）*：对于任何分隔 $U_t$ 与 $S_t$ 的割 $\Omega$，诱导容量为 $C_\text{cut}(\Omega) = \sup_{p(X_\Omega \mid \tilde T_t)} I(X_\Omega \to Y_{\Omega^c} \mid \tilde T_t, X_{\Omega^c})$，则有
\[
  H(S_t \mid \tilde T_t) \;\leq\; \underbrace{H(S_t \mid T_t)}_{\varepsilon_\text{nominal}} \;+\; \min_{\Omega} C_\text{cut}(\Omega).
\]
令 $\varepsilon_{\text{state}}^{\text{UB}} := \varepsilon_\text{nominal} + \min_\Omega C_\text{cut}(\Omega)$，则 $\varepsilon_\text{state} \leq \varepsilon_{\text{state}}^{\text{UB}}$。

这里 $X_\Omega$ 表示进入跨越割的边的输入信号，$Y_{\Omega^c}$ 表示相应的输出信号，$X_{\Omega^c}$ 表示接收端的边界状态（形式化定义见附录~\ref{app:netinfo}）。

*推论（加性形式）*：在软件正交性下，$\varepsilon_{\text{state}}^{\text{UB}} = \varepsilon_\text{nominal} + \min_{C \in \mathcal{C}_\text{unlogged}} \sum_{e \in C} c_e$，即未记录子图上的离散最小割。

*证明概要：* 链式法则给出 $H(S_t \mid \tilde T_t) = H(S_t \mid T_t) + I(S_t; M_t \mid \tilde T_t)$，其中 $M_t = T_t \setminus \tilde T_t$。从 $U_t$ 到 $S_t$ 的每条路径均跨越某个割 $\Omega$，因此 $M_t$ 被跨割信号 $d$-分离于 $S_t$；DPI 给出 $I(S_t; M_t \mid \tilde T_t) \leq C_\text{cut}(\Omega)$。对割取最小化并代入引理即完成证明（完整推导见附录~\ref{app:netinfo}）。

*推论（自回归零割）*：如果系统是一个严格的自回归核心且 $\tilde T_t$ 包含完整的上下文窗口，则 $\mathcal{C}_\text{unlogged} = \varnothing$，每个割的诱导容量为零，且 $\varepsilon_{\text{state}}^{\text{UB}} = 0$。

## 五、动态证书：通过条件 DPI 的决策相关性

动态证书针对 $\delta_\text{act} := I(S_t; A_t \mid \tilde T_t)$。由于 $S_t$ 不可观测，我们指定其测量变量在给定 $\tilde T_t$ 下满足 $X_t \to S_t \to A_t$ 的探针。条件 DPI 提供正确性论证：$I(X_t; A_t \mid \tilde T_t) \leq \delta_\text{act}$。

*命题（基于条件 DPI 的探针证书）*：对于任何在给定 $\tilde T_t$ 下满足 $X_t \to S_t \to A_t$ 的可容许探针变量 $X_t$，探针测量 $I(X_t; A_t \mid \tilde T_t)$ 是 $\delta_\text{act}$ 的一个有效下界证书。

**重放证书。** 令 $R_t \in \{\text{wild}, \text{replay}\}$ 表示一个缺失状态片段是否在同一条可见轨迹 $\tilde T_t$ 下被重建（受控重新执行，而非转述变化）。则 $I(R_t; A_t \mid \tilde T_t) = \mathrm{JS}(P_\text{wild}, P_\text{replay} \mid \tilde T_t) \leq \delta_\text{act}$。离散行动空间允许对已实现行动或模型报告的行动概率进行直接的经验 JS 估计；下文实验会说明使用哪种方法。

**干预证书。** 令 $\xi_\text{hidden}$ 为对可疑未记录模块（缓存、内存缓冲区、草稿板）的外生扰动。如果在给定 $\tilde T_t$ 下满足 $\xi_\text{hidden} \to S_t \to A_t$，则 $I(\xi_\text{hidden}; A_t \mid \tilde T_t) \leq \delta_\text{act}$。离散行动空间允许直接的条件行动分布偏移估计（如 JS 散度）；对于连续行动空间，可使用 InfoNCE 或 MINE。需要灰盒扰动访问，是三种探针中最直接的因果探针。

**代理证书。** 令 $Z_t = f(S_t)$ 为有效状态的一个可读粗化（工具 logit 投影、注意力汇总）。由于在给定 $\tilde T_t$ 下 $Z_t \leftarrow S_t \to A_t$，条件 DPI 给出 $I(Z_t; A_t \mid \tilde T_t) \leq \delta_\text{act}$。我们通过拟合预测器 $p(A_t \mid \tilde T_t)$ 和 $p(A_t \mid \tilde T_t, Z_t)$ 并取其交叉熵缺口来估计该量，记为 $\hat I(Z_t; A_t \mid \tilde T_t)$。

**聚合。** 单个证书类别可能遗漏某些因果路径。定义 $\delta_{\text{act}}^{\text{LB}} := \max\{ I(R_t; A_t \mid \tilde T_t), I(\xi_\text{hidden}; A_t \mid \tilde T_t), I(Z_t; A_t \mid \tilde T_t) \}$。由最大值的单调性，聚合结果仍然是 $\delta_\text{act}$ 的一个有效下界。

**激活剖面。** 标量证书是可容许探针索引族的最大值。保留索引即得到一个*激活剖面*
\[
  \Delta(j) := I(X_t^{(j)}; A_t \mid \tilde T_t),
\]
其中 $j$ 可表示草稿板字段、去噪步骤、激活层或通信边。静态证书标识残差容量可能所在的位置；激活剖面标识这些容量在何处被行为性地使用。下文的实验保持这一代数结构不变，仅改变索引：ReAct 中为模块，扩散 LM 中为时间步，多智能体设置中为通信边。

## 六、经验诊断

实验从一个标量日志消融开始，然后追问动态信号出现在何处。静态消融（§\ref{sec:exp-static}）使用推论~\ref{cor:additive-ub} 从拓扑计算残差位预算。ReAct 干预和受控重放（§\ref{sec:exp-intervention}）表明同一未记录草稿板容量在计算器任务上休眠、在规划任务上活跃。§\ref{sec:diffusion-dynamic} 中的 LLaDA 探针按去噪步骤索引 $\Delta(j)$；§\ref{sec:multi-agent-private-report} 中的多智能体探针按私人对等报告边索引它。只读代理和人工合成真实校准见附录~\ref{app:proxy-bias} 和~\ref{app:synthetic}。所有流程均在单个 M4 Max 工作站上设计运行。

### 6.1 静态证书与日志消融

从 Qwen2.5-7B-Instruct ReAct 执行轨迹中提取时间展开 DAG，为每条未记录边分配预算 $c_e$（§\ref{sec:static-cert}）；未记录边上的最小割给出 $\varepsilon_{\text{state}}^{\text{UB}}$。日志记录的逐步加入将上界从 $16{,}464$ 位降至 $0$ 位。主导瓶颈是草稿板读取路径（$16{,}384$ 位）。同一静态计算也为后续扩散 LM 和多智能体动态检验提供了坐标系统。

### 6.2 动态因果证书：干预与受控重放

在相同拓扑下分离休眠/活跃任务：未记录草稿板在两种情形下都存在，但对计算器任务无关，对规划任务则是必要的。干预扰动草稿板（掩码或替换）；受控重放在保持 $\tilde T_t$ 不变的情况下彻底移除它。干预手段显示：掩码 $0.7$ 条件下规划任务的 JS 散度为 $0.0215$ 位（95\% CI $[0.0094,0.0410]$），计算器任务为零。受控重放中规划任务上 JS 散度为 $0.0163$ 位（95\% CI $[0.0124,0.0208]$），计算器任务为零。

在该固定拓扑下，未记录草稿板在两种任务划分中均对 $\varepsilon_{\text{state}}^{\text{UB}}$ 贡献 $16{,}384$ 位，与从提取的 ReAct DAG 得到的最小割一致。结构不可恢复性由部署边界和日志策略决定；残差决策相关性取决于任务使用的隐藏信道。

### 6.3 扩散 LM 上的时间证书分析

使用 LLaDA-8B-Instruct 在 $K=10$ 步去噪轨迹上，在步骤 $\{2,4,6,8,10\}$ 处对第 1 层激活施加高斯扰动（$\sigma{=}5.0$）。模式为「晚期绑定」（late-binding）：步骤 2--8 保持在低位（$0.001$--$0.006$ 位），而步骤 10 升至 $0.110$ 位（95\% CI $[0.052,0.234]$）。在证书几何中，LLaDA 在去噪全程携带隐藏容量；当去噪状态绑定到离散工具选择时，该容量变得与行动相关。

### 6.4 多智能体私人报告干预

多智能体设置再次改变索引。控制者将证据收集委托给 Worker，Worker 的私人报告不是辅助草稿板，而是决策图中的认识论边。主要干预将 Worker 报告替换为来自相反任务类别的报告，同时保持控制者协议固定。对照条件包括中性重放、同类洗牌和 Oracle 标签。

跨事实证据达到 $0.901$ 位（95\% CI $[0.873,0.928]$），接近 Oracle 上界 $1.000$ 位；同类洗牌仅为 $0.084$ 位。该对比是拓扑性的：在多智能体部署中，控制者的决策通过私人 Worker 报告路由，因此活跃位点是通信边本身。

## 七、讨论

**一张图：先看容量，再看激活。**

实验是一次连续的递进。静态证书首先绘制隐藏容量可能位于何处：草稿板模块、去噪接口、对等状态边。动态证书随后追问这些位置中哪些影响了行动。在 ReAct 中，同一草稿板在计算器任务上休眠，在规划任务上活跃。在 LLaDA 中，残差容量贯穿去噪全程，但行动相关性集中在晚期绑定步骤。在多智能体部署中，委托使私人 Worker 报告成为活跃边。

因此，效应量排序是坐标上的激活剖面，而非探针间的矛盾。在该协议下，声称一个未观测变量因果性地影响行为，必须同时在 $\varepsilon_{\text{state}}^{\text{UB}}$ 中标识一个信道和在 $\delta_{\text{act}}^{\text{LB}}$ 中标识一个探针。

## 致谢

我们感谢 Qwen2.5 和 LLaDA 的开发者为 ReAct 和扩散 LM 实验提供开源权重模型；感谢 GSM8K 和 HotpotQA 的创建者和维护者为多智能体设置提供基准数据；以及感谢 Hugging Face Transformers、PyTorch、NumPy、scikit-learn、NetworkX、Matplotlib、Lean 4、Lake 和 Mathlib 社区为实验、图表和形式化提供软件基础设施。所有计算在单台 Apple M4 Max 工作站上完成。

## 参考文献

[参考文献不做翻译，保持原文]

## 术语对照表

| 中文 | English | 备注 |
|------|---------|------|
| 双重证书 | dual certificate | 本文核心概念 |
| 静态证书 | static certificate | $\varepsilon_{\text{state}}^{\text{UB}}$ |
| 动态证书 | dynamic certificate | $\delta_{\text{act}}^{\text{LB}}$ |
| 结构不可恢复性 | structural unrecoverability | |
| 残差隐状态熵 | residual hidden-state entropy | |
| 决策相关性 | decision relevance | |
| 条件数据处理不等式 | conditional Data Processing Inequality (DPI) | |
| 割集上界 | cut-set bound | 来自网络信息论 |
| 软件正交性 | software orthogonality | |
| 时间展开有向无环图 | time-unrolled DAG | |
| 激活剖面 | activation profile | |
| 受控重放 | controlled replay | |
| 日志消融 | logging ablation | |
| 自回归零割 | autoregressive zero-cut | |
| 探针分类体系 | probe taxonomy | |
| 晚期绑定 | late-binding | LLaDA 结果 |
| 最小割 | min-cut | |
| 隐藏信道 | hidden channel | |
