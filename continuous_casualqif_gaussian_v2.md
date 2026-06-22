# Continuous CasualQIF over Linear-Gaussian SCMs, v2

This note preserves the new layered proposal first, then gives an edited
version. The main edit is to separate three notions that should not be collapsed:

```text
static Fisher information under a cut sigma-algebra
KL/Bregman projection geometry in exponential families
dynamic entropy contraction along OU/Fokker-Planck flow
```

The bridge between them is Gaussian-specific: de Bruijn / I-MMSE identities.

## 1. Original Layered Proposal

命题 A (静态, 层 1-4):

设 `G subset F` 是 cut 处的 sub-sigma-代。则在 exp family 流形
`(Theta, g_FR)` 上, m-投影

```text
pi_G : P -> P_G
```

满足 Pythagorean, 且 `d_FR(P, P_G)` 的对偶 Bregman 表示为

```text
D(P || P_G) = I_F(theta) - I_G(theta)
```

之 KL 化身。在 Cramer-Rao 下界意义上, 由 Fisher 信息差
`I_F - I_G` 控制。

作者谱系:

```text
Fisher / Rao / Chentsov / Amari
```

与 Fokker-Planck 无关。

命题 B (动态, 层 5-6):

设 `{T_t}` 是 OU 半群, 即 Fokker-Planck 解算子, `gamma` 是不变 Gaussian。
则

```text
D(T_t P_0 || gamma) <= e^{-2t} D(P_0 || gamma)
```

这是 Bakry-Emery `K = 1` 情形。

作者谱系:

```text
Fokker-Planck / Bakry-Emery
```

与 cut sigma-代无关。

桥 (层 7, de Bruijn):

```text
(d/dt) D(T_t P_0 || gamma) = -(1/2) I(T_t P_0 || gamma)
```

这一条把 cut 处 Fisher 瓶颈, 即命题 A 的右端, 与沿流衰减率, 即命题 B 的指数,
绑成同一数量。

容量陈述 (层 8, Shannon):

若 cut 由加性 Gaussian noise 实现, 则

```text
C_cut = (1/2) log(1 + SNR_cut)
```

由 de Bruijn 恒等式直接积分得到。

关键: 哪里不能交换次序。

```text
层 1 -> 层 6 不能跳。
没有层 5 (Fokker-Planck 半群) 之前, "沿流" 是无意义符号。

层 4 -> 层 8 不能跳。
没有层 7 (de Bruijn), I(X;Y) 与 Fisher I(theta) 是同名异物。

层 3 -> 层 4 单向。
Amari 流形支撑投影算法; 但层 4 不蕴含层 3 外的几何。
```

实践含义: 论文写 continuous `stateLeakage_le_cutCapacity` 时, 必须显式分两段:

```text
(A) cut capacity bound:  static, 引用 Csiszar-Tusnady / Amari projection
(B) flow contraction:    dynamic, 引用 Bakry-Emery
(bridge) 若两者要相等:    引用 de Bruijn, 要求 Gaussian / OU
```

计算骨架:

```text
0. 测度论底座:
   Kolmogorov 1933
   给: (V, F, P_theta), 条件期望 E[.|G] for G subset F
   止于: 无统计结构, theta 只是 index
   接下: 选定参数族 {P_theta : theta in Theta}, 引入 score function

1. Fisher 信息:
   Fisher 1925 / Cramer 1946 / Rao 1945
   给: I(theta) = E_theta[score score^T]
       Cramer-Rao: Cov(theta_hat) >= I(theta)^{-1}
       DPI: I_G(theta) <= I_F(theta) for G subset F
   止于: 标量/矩阵不等式, 不是几何对象
   接下: 把 I(theta) 当成 Theta 上的 Riemannian metric tensor

2. Fisher-Rao 几何:
   Rao 1945 / Chentsov 1972
   给: (Theta, g_FR), Chentsov 唯一性, geodesic distance
   止于: 只有 metric, 没有 affine connection / 平行移动
   接下: 引入 alpha-connections, 选 alpha = +/-1 得对偶平坦

3. 对偶平坦 / exp family:
   Amari 1985, Amari-Nagaoka 2000
   给: 双坐标, KL = Bregman, Pythagorean, projection theorem
   止于: 静态。描述流形结构, 不描述演化
   接下: 让 Markov 算子作用于流形上的点, 进入动力学

4. 静态 DPI / 容量算法:
   Csiszar-Tusnady 1984, Blahut 1972, Arimoto 1972
   给: alternating I-projection, C = sup I(X;Y), KKT projection fixed point
   止于: 固定信道。无时间演化
   接下: 时间相关信道 / 连续时间流, 需要测度空间上的 PDE

5. Fokker-Planck / Markov 半群:
   Fokker 1914, Planck 1917, Kolmogorov 1931, Hille-Yosida 1948
   给: partial_t P_t = L^* P_t, T_t = e^{tL}, 不变测度 gamma
   止于: 纯动力学。无 Lyapunov 单调性陈述
   接下: 选 D(.||gamma) 作 Lyapunov 函数, 需要 curvature 条件

6. Bakry-Emery Gamma_2:
   Bakry-Emery 1985
   给: CD(K, infinity), KL 指数收缩, log-Sobolev
   止于: 要求扩散半群 + 充分正则性
   接下: 在 OU 情形 K=1, 把 Fisher 信息联回动态衰减率

7. de Bruijn 恒等式 + Stam 不等式:
   Stam 1959, de Bruijn via Stam
   给: entropy derivative = Fisher information along heat / OU flow
   止于: 必须 heat / OU semigroup。一般 Markov 不成立
   接下: Fisher 与 entropy time-derivative 的桥

8. 信道容量:
   Shannon 1948
   给: C = sup I(X;Y)
       Gaussian channel C = (1/2) log(1 + SNR)
   止于: 容量是 operational 量, 与 error 概率挂钩需 coding theorem
   接下: 在 SCM cut 上, cut capacity = sub-sigma-代约束下的 Shannon 容量
```

## 2. Edited Version

The layered architecture is right, but proposition A should be split. The static
cut, the Amari projection theorem, and the capacity algorithm are adjacent
facts, not one identity.

The corrected thesis is:

```text
Static cuts produce Fisher-information loss.
Exponential-family geometry represents KL as Bregman divergence and gives
projection Pythagorean identities.
Capacity tightness comes from Csiszar-Tusnady / Blahut-Arimoto, with Gaussian
water-filling as the closed-form specialization.
Dynamic contraction is a separate OU/Bakry-Emery theorem.
de Bruijn / I-MMSE is the Gaussian bridge between Fisher dissipation and
Shannon mutual information.
```

## 3. Corrected Proposition A: Static Cut

Let `(Omega, F, P_theta)` be a dominated statistical model with score

```text
s_F(theta) = partial_theta log p_theta
```

and let `G subset F` be the cut sigma-algebra. The observable score is the
conditional expectation:

```text
s_G(theta) = E_theta[s_F(theta) | G]
```

Therefore:

```text
I_G(theta) = E_theta[s_G(theta) s_G(theta)^T]
I_F(theta) = E_theta[s_F(theta) s_F(theta)^T]
I_G(theta) <= I_F(theta)
```

in Loewner order. More precisely:

```text
I_F(theta) - I_G(theta)
  = E_theta[ Var_theta(s_F(theta) | G) ]
```

This is the static Fisher DPI for a cut. It is a statement about
coarse-graining. It does not require Fokker-Planck, OU flow, or Bakry-Emery.

Equality holds iff the full score is already `G`-measurable:

```text
s_F(theta) = E_theta[s_F(theta) | G]
```

so the cut loses no local statistical information.

## 4. Fisher Difference Is Not a Global KL Gap

The unsafe statement is:

```text
D(P || P_G) = I_F(theta) - I_G(theta)
```

This should not be used as a global identity. The safe statement is
infinitesimal:

```text
D(P_theta || P_{theta + dtheta})
  = 1/2 dtheta^T I_F(theta) dtheta + o(|dtheta|^2)
```

After coarse-graining to `G`:

```text
D(P_theta^G || P_{theta + dtheta}^G)
  = 1/2 dtheta^T I_G(theta) dtheta + o(|dtheta|^2)
```

Thus:

```text
I_F(theta) - I_G(theta)
```

is the Hessian-level, local KL information loss induced by the cut. It is the
second-order shadow of a KL/Bregman projection gap, not the global KL gap itself.

## 5. Corrected Proposition A2: Information Geometry

In a regular exponential family:

```text
p_theta(x) = exp(theta · T(x) - psi(theta)) h(x)
```

the Fisher information is:

```text
I(theta) = Hessian psi(theta)
```

and KL divergence is the Bregman divergence of the log-partition potential:

```text
D(p_theta || p_theta')
  = B_psi(theta', theta)
```

With the dual coordinates:

```text
theta = natural coordinates
eta   = expectation coordinates
```

the e- and m-connections make the model dually flat. Projection Pythagorean
identities hold under the usual regularity and convexity conditions, for
example when the target constraint set is e-flat or m-flat and the projection
exists uniquely.

So the Amari statement should be:

```text
In the dually flat exponential-family setting, the cut-induced approximation
problem can be represented as a KL/Bregman projection problem, and the
projection gap obeys a Pythagorean identity.
```

This is stronger than Fisher DPI, but it needs more structure than a bare
sub-sigma-algebra.

## 6. Corrected Proposition A3: Tightness Algorithm

For a fixed channel, capacity is:

```text
C = sup_{p_X} I(X;Y)
```

Blahut-Arimoto and Csiszar-Tusnady alternating I-projection give a computable
projection algorithm with convergence to the optimizing distribution under the
standard finite or regular convex assumptions.

KKT conditions alone say:

```text
at an optimizer, the stationarity equations hold
```

They do not by themselves answer:

```text
how do we find the optimizer?
why is the proposed C tight?
```

The projection algorithm does answer this. In the Gaussian specialization, the
algorithm degenerates to water-filling.

## 7. Gaussian Specialization

For a Gaussian cut channel:

```text
Y = A X + N
N ~ N(0, Sigma_N)
X ~ N(0, Sigma_X)
```

the mutual information is:

```text
I(X;Y)
  = 1/2 log det(I + Sigma_N^{-1/2} A Sigma_X A^T Sigma_N^{-1/2})
```

Under a trace or covariance constraint on `Sigma_X`, maximizing this expression
gives water-filling. In the scalar or diagonalized channel:

```text
C_cut = 1/2 sum_i log(1 + P_i / N_i)
```

and in the scalar case:

```text
C_cut = 1/2 log(1 + SNR_cut)
```

This is the cleanest answer to the reviewer question:

```text
Why is C tight?
```

Answer:

```text
Because the Gaussian channel capacity problem is solved exactly by
water-filling, which is the Gaussian specialization of the projection /
Blahut-Arimoto picture.
```

## 8. Corrected Proposition B: Dynamic OU Contraction

The dynamic theorem starts only after introducing a Markov semigroup. For the
standard OU generator:

```text
L = Delta - x · grad
```

with invariant standard Gaussian `gamma`, the semigroup `T_t = exp(tL)` satisfies
Bakry-Emery `CD(1, infinity)`. Therefore:

```text
D(T_t P || gamma) <= e^{-2t} D(P || gamma)
```

under the standard regularity assumptions.

This statement is independent of a cut sigma-algebra. It is about entropy
dissipation along time, not about observing less of the sample space.

## 9. de Bruijn / I-MMSE Bridge

The bridge is not a general identity between parameter Fisher information and
Shannon capacity. It is Gaussian-flow-specific.

For the OU convention:

```text
L = Delta - x · grad
```

the entropy dissipation identity is typically normalized as:

```text
d/dt D(T_t P || gamma) = - I_rel(T_t P || gamma)
```

where `I_rel` is relative Fisher information:

```text
I_rel(P || gamma)
  = integral |grad log(dP/dgamma)|^2 dP
```

Other heat-flow conventions insert a factor `1/2`. The paper must fix one
normalization and use it consistently; otherwise the claimed `e^{-2t}` rate and
the `1/2` in de Bruijn will conflict.

The conceptual bridge is:

```text
Fisher information controls infinitesimal entropy decay along Gaussian noise /
OU flow.
```

For Gaussian channels, integrating this relation, together with maximum entropy
or I-MMSE identities, yields the log-det capacity formula.

## 10. Non-Commutation Rules

These are the rules that should be explicit in the paper.

```text
Layer 1 -> Layer 6 cannot jump.
Before a Markov semigroup exists, "along the flow" is not meaningful.

Layer 4 -> Layer 8 cannot jump.
Before de Bruijn / I-MMSE, Fisher information and Shannon mutual information
are related only locally or by analogy.

Layer 3 -> Layer 4 is one-way.
Information geometry supplies projection structure, but the convergence and
capacity algorithm need Csiszar-Tusnady / Blahut-Arimoto assumptions.

Layer 6 -> Layer 8 cannot jump.
OU entropy contraction does not by itself give operational channel capacity.
Capacity still needs a channel model and a coding/information-theoretic
interpretation.
```

## 11. Paper-Level Structure

The continuous version of `stateLeakage_le_cutCapacity` should be written in
three explicit steps.

Step A, static cut:

```text
G subset F
=> score_G = E[score_F | G]
=> I_G <= I_F
```

Step B, capacity tightness:

```text
for a fixed Gaussian cut channel
=> I(X;Y) has the log-det form
=> water-filling attains the supremum
=> C_cut is tight
```

Step C, dynamic contraction:

```text
for OU flow with invariant gamma
=> KL contracts exponentially by Bakry-Emery
```

Bridge:

```text
if the cut/noise is Gaussian and the flow is heat/OU
=> de Bruijn / I-MMSE identifies Fisher dissipation with entropy derivative
=> static bottleneck and dynamic decay are two faces of the same Gaussian
   information geometry
```

## 12. Lean Boundary

The formalization should not begin with full continuous measure-theoretic DPI.
The tractable core is:

```text
finite-dimensional real matrices
positive semidefinite / positive definite covariance matrices
Loewner order
Gaussian covariance pushforward:
  Sigma_Y = A Sigma_X A^T + Sigma_N
log-det mutual information formula
conditional covariance zero criterion for Gaussian CI
matrix form of water-filling as an optimization theorem interface
```

The measure-theoretic layer can be imported only where needed:

```text
GaussianMeasure
Radon-Nikodym derivative for dominated Gaussian families
conditional expectation for sub-sigma-algebras
```

Avoid making Bochner integration the first bottleneck. First prove the Gaussian
matrix algebra that the paper actually needs.

## 13. One-Line Version

Continuous CasualQIF should separate static cuts from dynamic flows: a cut
sub-sigma-algebra gives Fisher information loss, exponential-family projection
geometry gives KL/Bregman tightness algorithms, Gaussian water-filling gives a
tight cut capacity, and OU/Bakry-Emery gives an independent entropy contraction
theorem connected to capacity only through Gaussian de Bruijn / I-MMSE bridges.
